import logging
from decimal import Decimal

from django.db.models import QuerySet

from activity.exceptions.activity_exceptions import TrackIDDoesNotExists


class ActivityAggregator:
    @staticmethod
    def aggregate(activities: QuerySet) -> dict:
        try:
            last_status = activities[0].status
            track_id = activities[0].track_id
        except IndexError:
            logging.error("No such activities in db")
            raise TrackIDDoesNotExists

        amount = Decimal(0.0)
        for activity in activities[::-1]:
            if activity.status == "S":
                amount = amount + Decimal(activity.billig_amount)
            elif activity.status == "R":
                amount = amount - Decimal(activity.billig_amount)
        return {
            "track_id": track_id,
            "last_status": last_status,
            "amount": amount,
        }


activity_aggregator = ActivityAggregator()
