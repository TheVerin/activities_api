from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from activity.exceptions.activity_exceptions import (
    CannotCalculateAmount,
    TrackIDDoesNotExists,
)
from activity.models import Activity
from activity.tools.aggregators import activity_aggregator


class ActivityAggregationTest(TestCase):
    def setUp(self) -> None:
        self.detail_view = "activity_aggregate"

        self.client = APIClient()

        self.activity = Activity.objects.create(
            id="X13200000Z",
            activity_date="2021-04-16T08:05:35.941465",
            track_id="T123456",
            status="S",
            billing_amount=Decimal(10.54),
        )
        Activity.objects.create(
            id="X13200001Z",
            activity_date="2021-04-16T08:05:36.941465",
            track_id="T123456",
            status="A",
            billing_amount=Decimal(10.54),
        )
        Activity.objects.create(
            id="X13200002Z",
            activity_date="2021-04-16T08:05:37.941465",
            track_id="T123456",
            status="R",
            billing_amount=Decimal(0.54),
        )
        Activity.objects.create(
            id="X13200003Z",
            activity_date="2021-04-16T08:05:38.941465",
            track_id="T123456",
            status="S",
            billing_amount=Decimal(10.00),
        )
        Activity.objects.create(
            id="X13200004Z",
            activity_date="2021-04-16T08:05:39.941465",
            track_id="T123456",
            status="A",
            billing_amount=Decimal(10.54),
        )

    def test_cannot_get_track_id(self):
        response = self.client.get(reverse(self.detail_view, kwargs={"track_id": "11"}))
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"message": "Track ID 11 does not exists"})

    def test_aggregate_activity(self):
        response = self.client.get(
            reverse(self.detail_view, kwargs={"track_id": self.activity.track_id})
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "track_id": self.activity.track_id,
                "last_status": "A",
                "amount": Decimal(20.00),
            },
        )

    def test_aggregator_id_does_not_exists(self):
        activities = Activity.objects.filter(track_id="11").order_by("-activity_date")
        try:
            activity_aggregator.aggregate(activities=activities)
        except TrackIDDoesNotExists:
            self.assertTrue("Works fine")

    def test_aggregator_correct_response(self):
        activities = Activity.objects.filter(track_id=self.activity.track_id).order_by(
            "-activity_date"
        )
        data = activity_aggregator.aggregate(activities=activities)
        self.assertEqual(
            data,
            {
                "track_id": self.activity.track_id,
                "last_status": "A",
                "amount": Decimal(20.00),
            },
        )
