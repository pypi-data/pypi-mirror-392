from solo.models import SingletonModel

from django.db import models
from django.utils.translation import gettext as _

from allianceauth.eveonline.models import (
    EveAllianceInfo, EveCharacter, EveCorporationInfo,
)


class AlumniSetup(SingletonModel):
    alumni_corporations = models.ManyToManyField(
        EveCorporationInfo,
        blank=True,
        help_text=_("Characters with these Corps in their History will be given Alumni Status"))
    alumni_alliances = models.ManyToManyField(
        EveAllianceInfo,
        blank=True,
        help_text=_("Characters with these Alliances in their History will be given Alumni Status"))

    def __str__(self) -> str:
        return _("Alumni Config")

    class Meta:
        verbose_name = _("Alumni Config")


class CorporationUpdateTimestamp(models.Model):
    corporation_id = models.PositiveIntegerField(unique=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Corporation Update Timestamp")
        verbose_name_plural = _("Corporation Update Timestamps")


class CharacterUpdateTimestamp(models.Model):
    character = models.OneToOneField(EveCharacter, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Character Update Timestamp")
        verbose_name_plural = _("Character Update Timestamps")


class CorporationAllianceHistory(models.Model):
    corporation_id = models.PositiveIntegerField(db_index=True)
    alliance_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    is_deleted = models.BooleanField(
        default=False,
        help_text=_("True if the corporation has been deleted"))
    record_id = models.PositiveIntegerField(
        help_text=_("An incrementing ID that can be used to canonically establish order of records in cases where dates may be ambiguous"))
    start_date = models.DateTimeField()

    class Meta:
        verbose_name = _("Corporation/Alliance History")
        verbose_name_plural = _("Corporation/Alliance Histories")
        constraints = [
            models.UniqueConstraint(fields=['corporation_id', 'record_id'], name="CorporationAllianceRecord"),
        ]


class CharacterCorporationHistory(models.Model):

    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE)
    corporation_id = models.PositiveIntegerField()
    is_deleted = models.BooleanField(
        default=False,
        help_text=_("True if the corporation has been deleted"))
    record_id = models.PositiveIntegerField(
        help_text=_("An incrementing ID that can be used to canonically establish order of records in cases where dates may be ambiguous"))
    start_date = models.DateTimeField()

    class Meta:
        verbose_name = _("Character/Corporation History")
        verbose_name_plural = _("Character/Corporation Histories")
        constraints = [
            models.UniqueConstraint(fields=['character', 'record_id'], name="CharacterCorporationRecord"),
        ]
