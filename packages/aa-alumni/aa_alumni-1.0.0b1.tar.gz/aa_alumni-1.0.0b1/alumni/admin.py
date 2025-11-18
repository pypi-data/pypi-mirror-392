from solo.admin import SingletonModelAdmin

from django.contrib import admin

from .models import (
    AlumniSetup, CharacterCorporationHistory, CharacterUpdateTimestamp,
    CorporationAllianceHistory, CorporationUpdateTimestamp,
)


@admin.register(AlumniSetup)
class AlumniSetupAdmin(SingletonModelAdmin):
    filter_horizontal = ["alumni_corporations", "alumni_alliances"]


@admin.register(CorporationAllianceHistory)
class CorporationAllianceHistoryAdmin(admin.ModelAdmin):
    search_fields = ['corporation_id', 'alliance_id']
    list_display = ('corporation_id', 'alliance_id', 'record_id', 'start_date')


@admin.register(CharacterCorporationHistory)
class CharacterCorporationHistoryAdmin(admin.ModelAdmin):
    search_fields = ['corporation_id', 'character']
    list_display = ('corporation_id', 'character', 'record_id', 'start_date')


@admin.register(CharacterUpdateTimestamp)
class CharacterUpdateTimestampAdmin(admin.ModelAdmin):
    search_fields = ['character__character_name', 'character__character_id']
    list_display = ('character', 'last_updated')


@admin.register(CorporationUpdateTimestamp)
class CorporationUpdateTimestampAdmin(admin.ModelAdmin):
    search_fields = ['corporation_id']
    list_display = ('corporation_id', 'last_updated')
