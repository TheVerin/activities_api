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

from activity.models import Activity


class ActivityViewsTest(TestCase):
    def setUp(self) -> None:
        self.detail_view = "activity_aggregate"
        self.create_view = "activity_create"

        self.client = APIClient()

        self.activity = Activity.objects.create(
            id="1",
            activity_date="2021-04-16T08:05:35.941465",
            track_id="T123456",
            status="S",
            billig_amount=Decimal(10.54),
        )
        Activity.objects.create(
            id="2",
            activity_date="2021-04-16T08:05:36.941465",
            track_id="T123456",
            status="A",
            billig_amount=Decimal(10.54),
        )
        Activity.objects.create(
            id="3",
            activity_date="2021-04-16T08:05:37.941465",
            track_id="T123456",
            status="R",
            billig_amount=Decimal(0.54),
        )
        Activity.objects.create(
            id="4",
            activity_date="2021-04-16T08:05:38.941465",
            track_id="T123456",
            status="S",
            billig_amount=Decimal(10.00),
        )
        Activity.objects.create(
            id="5",
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

    def test_create_one_activity(self):
        payload = {
            "id": "6",
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
        with open("/src/activity/tests/json_files/activities.json") as payload_file:
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
        with open(
            "/src/activity/tests/json_files/activities_duplicated.json"
        ) as payload_file:
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

    def test_create_1000_activities(self):
        with open(
            "/src/activity/tests/json_files/activities_1000.json"
        ) as payload_file:
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
            "id": "1",
            "activity_date": "2021-04-16T09:14:16.435742",
            "track_id": "TRACK_ID_3",
            "status": "A",
            "billig_amount": 30,
        }
        response = self.client.post(reverse(self.create_view), data=payload)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Cannot store any activity"})

    def test_create_all_activities_already_in_db(self):
        payload = [
            {
                "id": "1",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
                "billig_amount": 30,
            },
            {
                "id": "2",
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
        self.assertEqual(response.data, {"message": "Cannot store any activity"})

    def test_create_activity_wrong_type_of_data(self):
        payload = {
            "id": "6",
            "activity_date": "2021-04-16T09:14:14",
            "track_id": "TRACK_ID_3",
            "status": 11,
            "billig_amount": "o",
        }
        response = self.client.post(reverse(self.create_view), data=payload)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Cannot store any activity"})

    def test_create_activity_lack_of_data(self):
        payload = {
            "id": "6",
            "activity_date": "2021-04-16T09:14:16.435742",
            "track_id": "TRACK_ID_3",
            "status": 11,
        }
        response = self.client.post(reverse(self.create_view), data=payload)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Cannot store any activity"})

    def test_create_all_activities_wrong_type_of_data(self):
        payload = [
            {
                "id": "6",
                "activity_date": "2021-04-16T09:14:11",
                "track_id": "TRACK_ID_3",
                "status": "p",
                "billig_amount": "q",
            },
            {
                "id": "7",
                "activity_date": "2021-04-16T09:14:11",
                "track_id": "TRACK_ID_3",
                "status": "p",
                "billig_amount": "q",
            },
        ]
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Cannot store any activity"})

    def test_create_all_activities_lack_of_data(self):
        payload = [
            {
                "id": "8",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
            },
            {
                "id": "9",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
            },
        ]
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Cannot store any activity"})

    def test_create_part_activities_wrong_type_of_data(self):
        payload = [
            {
                "id": "10",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
                "billig_amount": 10,
            },
            {
                "id": "11",
                "activity_date": "2021-04-16T09:14:11",
                "track_id": "TRACK_ID_3",
                "status": "p",
                "billig_amount": "q",
            },
        ]

        activities_count_before = Activity.objects.count()
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        activities_count_after = Activity.objects.count()

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(activities_count_before, activities_count_after - 1)

    def test_create_part_activities_lack_of_data(self):
        payload = [
            {
                "id": "12",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
                "billig_amount": 10,
            },
            {
                "id": "13",
                "activity_date": "2021-04-16T09:14:16.435742",
                "track_id": "TRACK_ID_3",
                "status": "A",
            },
        ]

        activities_count_before = Activity.objects.count()
        response = self.client.post(
            reverse(self.create_view),
            data=json.dumps(payload),
            content_type="application/json",
        )
        activities_count_after = Activity.objects.count()

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(activities_count_before, activities_count_after - 1)
