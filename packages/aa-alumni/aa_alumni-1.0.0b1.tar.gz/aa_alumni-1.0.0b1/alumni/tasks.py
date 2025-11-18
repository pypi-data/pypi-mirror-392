import typing
from datetime import datetime, timezone
from math import ceil
from random import randint

from celery import shared_task

from allianceauth.authentication.models import State
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import esi_rate_limiter_bucketed
from esi.exceptions import (
    ESIBucketLimitException, ESIErrorLimitException, HTTPNotModified,
)
from esi.rate_limiting import ESIRateLimitBucket

from .app_settings import (
    ALUMNI_CHARACTERCORPORATION_RATELIMIT, ALUMNI_STATE_NAME,
    ALUMNI_TASK_JITTER, ALUMNI_TASK_PRIORITY,
)
from .models import (
    AlumniSetup, CharacterCorporationHistory, CharacterUpdateTimestamp,
    CorporationAllianceHistory, CorporationUpdateTimestamp,
)
from .providers import (
    get_characters_character_id_corporationhistory,
    get_corporations_corporation_id_alliancehistory,
)

if typing.TYPE_CHECKING:
    from esi.stubs import AllianceID, CharacterID, CorporationID

logger = get_extension_logger(__name__)


def char_alliance_datecompare(alliance_id: "AllianceID", character_id: "CharacterID") -> bool:
    """Voodoo relating to checking start dates and _next_ start dates

    Necessary to determine if a character was a member of a corp
    WHILE it was in an alliance

    Parameters
    ----------
    alliance_id: int
        Should match an existing EveAllianceInfo model

    character_id: int
        Should match an existing EveCharacter model

    Returns
    -------
    bool
        Whether True"""

    character = EveCharacter.objects.get(character_id=character_id)
    char_corp_history = CharacterCorporationHistory.objects.filter(
        character=character).order_by('record_id')

    for index, char_corp_record in enumerate(char_corp_history):
        # Corp Joins Alliance, Between Char Join/Leave Corp
        try:
            filter_end_date = char_corp_history[index + 1].start_date
        except IndexError:
            filter_end_date = datetime.now(timezone.utc)

        if CorporationAllianceHistory.objects.filter(
            corporation_id=char_corp_record.corporation_id,
            alliance_id=alliance_id,
            start_date__range=(
                char_corp_record.start_date,
                filter_end_date)).exists() is True:
            return True

        corp_alliance_history = CorporationAllianceHistory.objects.filter(
            corporation_id=char_corp_record.corporation_id).order_by('record_id')

        for index_2, corp_alliance_record in enumerate(corp_alliance_history):
            # Needs to be unfiltered alliance id because we need _next_ start date
            # but check if the alliance id matches before we run any logic
            try:
                if corp_alliance_record.alliance_id == alliance_id:
                    # Char Joins Corp, Between Corp Join/Leave
                    if corp_alliance_record.start_date < char_corp_record.start_date < corp_alliance_history[index_2 + 1].start_date:
                        return True
                    # Char Leaves Corp, Between Corp Join/Leave
                    elif corp_alliance_record.start_date < char_corp_history[index + 1].start_date < corp_alliance_history[index_2 + 1].start_date:
                        return True
                    # Corp Leaves Alliance in between Char Join/Leave Corp
                    elif char_corp_record.start_date < corp_alliance_history[index_2 + 1].start_date < char_corp_history[index + 1].start_date:
                        return True
                    else:
                        pass
                else:
                    pass
            except Exception as e:
                # Need to actually add some IndexError handling to above tasks, but lets log this gracefully so as not to cactus up the whole thing.
                logger.exception(e)
    return False


@shared_task
def alumni_check_character(character_id: "CharacterID") -> bool:
    """Check/Update a characters alumni status using the historical models

    Parameters
    ----------
    character_id: int
        Should match an existing EveCharacter model

    Returns
    -------
    bool
        Whether the user is an alumni or not **it is updated in this function as well**"""

    alumni_setup = AlumniSetup.get_solo()
    alumni_state = State.objects.get(name=ALUMNI_STATE_NAME)
    character = EveCharacter.objects.get(character_id=character_id)

    if character.corporation_id in alumni_setup.alumni_corporations.values_list('corporation_id', flat=True):
        # Cheapo cop-out to end early
        alumni_state.member_characters.add(character)
        return True

    if character.alliance_id in alumni_setup.alumni_alliances.values_list('alliance_id', flat=True):
        # Cheapo cop-out to end early
        alumni_state.member_characters.add(character)
        return True

    for char_corp in CharacterCorporationHistory.objects.filter(character=character):
        if char_corp.corporation_id in alumni_setup.alumni_corporations.values_list('corporation_id', flat=True):
            # Less Cheap, but ending here is still better than the next one.
            alumni_state.member_characters.add(character)
            return True

    for alliance in alumni_setup.alumni_alliances.all():
        if char_alliance_datecompare(alliance_id=alliance.alliance_id, character_id=character_id):
            alumni_state.member_characters.add(character)
            return True

    # If we reach this point, we aren't an alumni
    alumni_state.member_characters.remove(character)
    return False


@shared_task
def run_alumni_check_all() -> None:
    for character in EveCharacter.objects.all().values('character_id'):
        alumni_check_character.apply_async(
            args=[character['character_id']],
            priority=ALUMNI_TASK_PRIORITY
        )  # pyright: ignore[reportFunctionMemberAccess, reportCallIssue]


@shared_task(bind=True, rate_limit=ALUMNI_CHARACTERCORPORATION_RATELIMIT)
def update_corporationalliancehistory(self, corporation_id: "CorporationID") -> None:
    """Update CorporationAllianceHistory models from ESI

    Parameters
    ----------
    corporation_id: int """

    if corporation_id <= 98000000:  # NPC Corps don't have CCH
        CorporationUpdateTimestamp.objects.update_or_create(
            corporation_id=corporation_id,
            defaults={'last_updated': datetime.now(timezone.utc)}
        )

    try:
        for cah in get_corporations_corporation_id_alliancehistory(corporation_id):
            CorporationAllianceHistory.objects.update_or_create(
                record_id=cah.record_id,
                corporation_id=corporation_id,
                alliance_id=cah.alliance_id,
                defaults={
                    'is_deleted': True if cah.is_deleted == 'true' else False,
                    'start_date': cah.start_date  # This can get adjusted by CCP i think
                }
            )
        CorporationUpdateTimestamp.objects.update_or_create(
            corporation_id=corporation_id,
            defaults={'last_updated': datetime.now(timezone.utc)}
        )
    except (ESIErrorLimitException, ESIBucketLimitException) as e:
        raise self.retry(exc=e, countdown=e.reset + 1 if e.reset is not None else 61, max_retries=3)
    except HTTPNotModified:
        CorporationUpdateTimestamp.objects.update_or_create(
            corporation_id=corporation_id,
            defaults={'last_updated': datetime.now(timezone.utc)}
        )
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, rate_limit=ALUMNI_CHARACTERCORPORATION_RATELIMIT)
@esi_rate_limiter_bucketed(bucket=ESIRateLimitBucket(*ESIRateLimitBucket.CHARACTER_CORPORATION_HISTORY))
def update_charactercorporationhistory(self, character_id: "CharacterID") -> None:
    """Update CharacterCorporationHistory models from ESI

    Parameters
    ----------
    character_id: int
        Should match an existing EveCharacter model"""

    try:
        character = EveCharacter.objects.get(character_id=character_id)
    except Exception as e:
        logger.exception(e)
        return
    if character.character_id <= 90000000:  # NPC Characters don't have CCH
        CharacterUpdateTimestamp.objects.update_or_create(
            character=character,
            defaults={'last_updated': datetime.now(timezone.utc)}
        )
    try:
        for cch in get_characters_character_id_corporationhistory(character_id):
            CharacterCorporationHistory.objects.update_or_create(
                character=character,
                corporation_id=cch.corporation_id,
                record_id=cch.record_id,
                defaults={
                    'is_deleted': True if cch.is_deleted == 'true' else False,
                    'start_date': cch.start_date
                }
            )
        CharacterUpdateTimestamp.objects.update_or_create(
            character=character,
            defaults={'last_updated': datetime.now(timezone.utc)}
        )
    except (ESIErrorLimitException, ESIBucketLimitException) as e:
        raise self.retry(exc=e, countdown=e.reset + 1 if e.reset is not None else 61)
    except HTTPNotModified:
        CharacterUpdateTimestamp.objects.update_or_create(
            character=character,
            defaults={'last_updated': datetime.now(timezone.utc)}
        )
    except Exception as e:
        logger.exception(e)


@shared_task
def update_models_subset(fraction: int = 14) -> None:
    """
    Update a subset of the CharacterCorporation history models from ESI.

    This task operates on 1/fraction of the oldest CCH and CAH records.

    At 1/14th, once a day this will update all Alumni records in two weeks.
    """

    # Force create all timestamps at zero if they don't exist
    character_timestamps = [
        CharacterUpdateTimestamp(
            character_id=character.id,
            last_updated=datetime.fromtimestamp(1, timezone.utc)) for character in EveCharacter.objects.all()]
    CharacterUpdateTimestamp.objects.bulk_create(character_timestamps, ignore_conflicts=True, batch_size=500)

    corporation_timestamps = [
        CorporationUpdateTimestamp(
            corporation_id=corp.corporation_id,
            last_updated=datetime.fromtimestamp(1, timezone.utc)) for corp in EveCorporationInfo.objects.all()]
    corporation_timestamps += [
        CorporationUpdateTimestamp(
            corporation_id=corp["corporation_id"],
            last_updated=datetime.fromtimestamp(1, timezone.utc)) for corp in CharacterCorporationHistory.objects.values('corporation_id').distinct()]
    CorporationUpdateTimestamp.objects.bulk_create(corporation_timestamps, ignore_conflicts=True, batch_size=500)

    for character in CharacterUpdateTimestamp.objects.all(
    ).order_by('last_updated')[:ceil(CharacterUpdateTimestamp.objects.count() / fraction)].values('character__character_id'):
        update_charactercorporationhistory.apply_async(
            args=[character['character__character_id']],
            priority=ALUMNI_TASK_PRIORITY,
            countdown=randint(1, ALUMNI_TASK_JITTER)
        )  # pyright: ignore[reportFunctionMemberAccess, reportCallIssue]

    for char_corp_record in CorporationUpdateTimestamp.objects.all(
    ).order_by('last_updated')[:ceil(CorporationUpdateTimestamp.objects.count() / fraction)].values('corporation_id'):
        update_corporationalliancehistory.apply_async(
            args=[char_corp_record['corporation_id']],
            priority=ALUMNI_TASK_PRIORITY,
            countdown=randint(1, ALUMNI_TASK_JITTER)
        )  # pyright: ignore[reportFunctionMemberAccess, reportCallIssue]


@shared_task()
def update_all_models() -> None:
    """Update All CharacterCorporation history models from ESI"""

    update_models_subset.apply_async(priority=ALUMNI_TASK_PRIORITY)  # pyright: ignore[reportFunctionMemberAccess, reportCallIssue]
