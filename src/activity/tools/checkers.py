from datetime import datetime
from decimal import Decimal

from activity.models import Activity


class ActivityChecker:
    def check_possibility_to_save(self, data: dict) -> bool:
        try:
            if Activity.objects.filter(id=data["id"]).exists() or not self._check_types(
                data=data
            ):
                return False
            return True
        except (KeyError, ValueError):
            return False

    @staticmethod
    def _check_types(data: dict) -> bool:
        if (
            isinstance(data["id"], str)
            and isinstance(
                datetime.strptime(data["activity_date"], "%Y-%m-%dT%H:%M:%S.%f"),
                datetime,
            )
            and isinstance(data["track_id"], str)
            and isinstance(Decimal(data["billig_amount"]), Decimal)
            and data["status"] in ["A", "S", "R"]
        ):
            return True
        return False


activity_checker = ActivityChecker()
