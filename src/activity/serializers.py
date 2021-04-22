from rest_framework.serializers import (
    CharField,
    ChoiceField,
    DecimalField,
    ModelSerializer,
    Serializer,
)

from activity.models import STATUSES, Activity


class ActivityAggregateSerializer(Serializer):
    track_id = CharField(max_length=10)
    amount = DecimalField(max_digits=8, decimal_places=2)
    last_status = ChoiceField(choices=STATUSES)


class ActivitySerializer(ModelSerializer):
    status = ChoiceField(choices=STATUSES)
    id = CharField(max_length=20)

    class Meta:
        model = Activity
        fields = (
            "id",
            "activity_date",
            "track_id",
            "status",
            "billig_amount",
        )
