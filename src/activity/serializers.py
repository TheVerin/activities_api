from rest_framework.serializers import CharField, ChoiceField, DecimalField, Serializer

from activity.models import STATUSES


class ActivityAggregateSerializer(Serializer):
    track_id = CharField(max_length=10)
    amount = DecimalField(max_digits=8, decimal_places=2)
    last_status = ChoiceField(choices=STATUSES)
