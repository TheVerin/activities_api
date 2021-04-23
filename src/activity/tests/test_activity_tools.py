from decimal import Decimal

from django.test import TestCase

from rest_framework.test import APIClient

from activity.exceptions.activity_exceptions import TrackIDDoesNotExists
from activity.models import Activity
from activity.tools.aggregators import activity_aggregator
from activity.tools.checkers import activity_checker


class ActivityToolsTest(TestCase):
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

    def test_checker_possible_to_save(self):
        payload = {
            "id": "X13210400Z",
            "activity_date": "2021-04-16T09:14:16.435742",
            "track_id": "TRACK_ID_3",
            "status": "A",
            "billig_amount": Decimal(11),
        }
        status = activity_checker.check_possibility_to_save(data=payload)
        self.assertTrue(status)

    def test_checker_already_in_db(self):
        payload = {
            "id": "X13210001Z",
            "activity_date": "2021-04-16T09:14:16.435742",
            "track_id": "TRACK_ID_3",
            "status": "A",
            "billig_amount": Decimal(11),
        }
        status = activity_checker.check_possibility_to_save(data=payload)
        self.assertFalse(status)

    def test_checker_wrong_type_of_data(self):
        payload = {
            "id": "X13210001Z",
            "activity_date": "2021-04-16T09:14:16.435742",
            "track_id": 11,
            "status": "B",
            "billig_amount": "4",
        }
        status = activity_checker.check_possibility_to_save(data=payload)
        self.assertFalse(status)

    def test_checker_invalid_payload(self):
        payload = {
            "id": "X13210400Z",
            "activity_date": "2021-04-16T09:14:16.435742",
            "track_id": "TRACK_ID_3",
            "status": "A",
        }
        status = activity_checker.check_possibility_to_save(data=payload)
        self.assertFalse(status)
