import typing

from allianceauth.services.hooks import get_extension_logger
from esi.openapi_clients import ESIClientProvider

from . import __esi_compatibility_date__, __title__, __url__, __version__

if typing.TYPE_CHECKING:
    from esi.stubs import (
        CharacterID, CharactersCharacterIdCorporationhistoryGetItem,
        CorporationID, CorporationsCorporationIdAlliancehistoryGetItem,
    )

esi = ESIClientProvider(
    compatibility_date=__esi_compatibility_date__,
    ua_appname=__title__,
    ua_version=__version__,
    ua_url=__url__,
    operations=[
        "GetCorporationsCorporationIdAlliancehistory",
        "GetCharactersCharacterIdCorporationhistory"]
)

logger = get_extension_logger(__name__)


def get_corporations_corporation_id_alliancehistory(corporation_id: "CorporationID") -> list["CorporationsCorporationIdAlliancehistoryGetItem"]:
    result = esi.client.Corporation.GetCorporationsCorporationIdAlliancehistory(
        corporation_id=corporation_id
    ).results()
    return result


def get_characters_character_id_corporationhistory(character_id: "CharacterID") -> list["CharactersCharacterIdCorporationhistoryGetItem"]:
    result = esi.client.Character.GetCharactersCharacterIdCorporationhistory(
        character_id=character_id
    ).results()
    return result
