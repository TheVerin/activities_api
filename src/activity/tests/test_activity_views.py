import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APIClient

from activity.exceptions.activity_exceptions import TrackIDDoesNotExists
from activity.models import Activity
from activity.tools.aggregators import activity_aggregator


class ActivityAggregationTest(TestCase):
    def setUp(self) -> None:
        self.detail_view = "activity_aggregate"
        self.create_view = "activity_create"

        self.client = APIClient()

        self.activity = Activity.objects.create(
            id="X13210000Z",
            activity_date="2021-04-16T08:05:35.941465",
            track_id="T123456",
            status="S",
            billig_amount=Decimal(10.54),
        )
        Activity.objects.create(
            id="X13210001Z",
            activity_date="2021-04-16T08:05:36.941465",
            track_id="T123456",
            status="A",
            billig_amount=Decimal(10.54),
        )
        Activity.objects.create(
            id="X13210002Z",
            activity_date="2021-04-16T08:05:37.941465",
            track_id="T123456",
            status="R",
            billig_amount=Decimal(0.54),
        )
        Activity.objects.create(
            id="X13210003Z",
            activity_date="2021-04-16T08:05:38.941465",
            track_id="T123456",
            status="S",
            billig_amount=Decimal(10.00),
        )
        Activity.objects.create(
            id="X13210004Z",
            activity_date="2021-04-16T08:05:39.941465",
            track_id="T123456",
            status="A",
            billig_amount=Decimal(10.54),
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

    def test_create_one_activity(self):
        payload = {
            "id": "X132110000Z",
            "activity_date": "2021-04-16T10:14:16.435742",
            "track_id": "TRACK_ID_3",
            "status": "A",
            "billig_amount": 30,
        }
        response = self.client.post(reverse(self.create_view), data=payload)
        from_db = Activity.objects.filter(id=payload["id"]).latest("activity_date")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(from_db.track_id, payload["track_id"])

    def test_create_multiple_activities(self):
        with open("/src/activity/tests/activities.json") as payload_file:
            payload = json.loads(payload_file.read())

        activities_count_before = Activity.objects.count()
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        activities_count_after = Activity.objects.count()

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(activities_count_before, activities_count_after - len(payload))

    def test_create_duplicated_activities(self):
        with open("/src/activity/tests/activities_duplicated.json") as payload_file:
            payload = json.loads(payload_file.read())

        activities_count_before = Activity.objects.count()
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        activities_count_after = Activity.objects.count()

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(activities_count_before, activities_count_after - 30)

    def test_create_10000_activities(self):
        with open("/src/activity/tests/activities_1000.json") as payload_file:
            payload = json.loads(payload_file.read())

        activities_count_before = Activity.objects.count()
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        activities_count_after = Activity.objects.count()

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(activities_count_before, activities_count_after - len(payload))

    def test_create_activity_already_in_db(self):
        payload = {
            "id": "X13210000Z",
            "activity_date": "2021-04-16T09:14:16.435742",
            "track_id": "TRACK_ID_3",
            "status": "A",
            "billig_amount": 30,
        }
        response = self.client.post(reverse(self.create_view), data=payload)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"message": f"Activity {payload['id']} already in db"}
        )

    def test_create_all_activities_already_in_db(self):
        payload = [
            {
                "id": "X13210000Z",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
                "billig_amount": 30,
            },
            {
                "id": "X13210001Z",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
                "billig_amount": 30,
            },
        ]
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "All activities are already in db"})
