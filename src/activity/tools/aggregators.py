from decimal import Decimal, InvalidOperation

from django.db.models import QuerySet

from activity.exceptions.activity_exceptions import (
    CannotCalculateAmount,
    TrackIDDoesNotExists,
)


class ActivityAggregator:
    @staticmethod
    def aggregate(activities: QuerySet) -> dict:
        try:
            last_status = activities[0].status
            track_id = activities[0].track_id
        except IndexError:
            raise TrackIDDoesNotExists

        amount = Decimal(0.0)
        for activity in activities[::-1]:
            try:
                if activity.status == "S":
                    amount = amount + Decimal(activity.billing_amount)
                elif activity.status == "R":
                    amount = amount - Decimal(activity.billing_amount)
                else:
                    continue
            except InvalidOperation:
                raise CannotCalculateAmount
        return {
            "track_id": track_id,
            "last_status": last_status,
            "amount": amount,
        }


activity_aggregator = ActivityAggregator()
