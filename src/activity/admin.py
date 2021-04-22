from django.contrib.admin import ModelAdmin, register

from csvexport.actions import csvexport

from activity.models import Activity


@register(Activity)
class ActivityAdmin(ModelAdmin):
    list_display = (
        "id",
        "track_id",
        "status",
    )
    ordering = ("activity_date", "billing_amount")
    search_fields = ("^id", "^track_id")
    actions = (csvexport,)
