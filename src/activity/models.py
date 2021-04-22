from django.db.models import CharField, DateTimeField, DecimalField, Model


STATUSES = [
    ("A", "A"),
    ("S", "S"),
    ("R", "R"),
]


class Activity(Model):
    id = CharField(max_length=20, editable=False, unique=True, primary_key=True)
    activity_date = DateTimeField()
    track_id = CharField(max_length=10)
    status = CharField(max_length=1, choices=STATUSES, blank=True)
    billing_amount = DecimalField(max_digits=8, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.id} {self.track_id} {self.status}"
