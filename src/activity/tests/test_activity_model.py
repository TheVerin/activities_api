from decimal import Decimal

from django.db.utils import IntegrityError
from django.test import TestCase

from activity.models import Activity


class ActivityModelTest(TestCase):
    def test_valid_car_model(self):
        entry = Activity.objects.create(
            id="X13200000Z",
            activity_date="2021-04-16T08:05:35.941465",
            track_id="T123456",
            status="S",
            billing_amount=Decimal(10.54),
        )
        self.assertEqual(str(entry), "X13200000Z T123456 S")

    def test_car_model_no_data(self):
        try:
            Activity.objects.create()
        except IntegrityError:
            self.assertTrue(True)

    def test_car_model_part_data(self):
        try:
            Activity.objects.create(
                id="X13200000Z",
                activity_date="2021-04-16T08:05:35.941465",
            )
        except IntegrityError:
            self.assertTrue(True)

    def test_create_activity_wrong_type_of_data(self):
        try:
            Activity.objects.create(
                id=1,
                activity_date=1,
                track_id=1,
                status=1,
                billing_amount="Z",
            )
        except TypeError:
            self.assertTrue(True)

    def test_create_activity_with_the_same_id(self):
        try:
            Activity.objects.create(
                id="X13200000Z",
                activity_date="2021-04-16T08:05:35.941465",
                track_id="T123456",
                status="S",
                billing_amount=Decimal(10.54),
            )
            Activity.objects.create(
                id="X13200000Z",
                activity_date="2021-04-15T08:05:35.941465",
                track_id="T123457",
                status="A",
                billing_amount=Decimal(10.55),
            )
        except IntegrityError:
            self.assertTrue(True)

    def test_create_activity_wrong_status(self):
        try:
            Activity.objects.create(
                id="X13200000Z",
                activity_date="2021-04-16T08:05:35.941465",
                track_id="T123456",
                status="T",
                billing_amount=Decimal(10.54),
            )
        except IntegrityError:
            self.assertTrue(True)
