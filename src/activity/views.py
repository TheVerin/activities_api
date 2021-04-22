from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from activity.exceptions.activity_exceptions import (
    CannotCalculateAmount,
    TrackIDDoesNotExists,
)
from activity.models import Activity
from activity.tools.aggregators import activity_aggregator


class ActivityRetrieveView(APIView):
    def get_queryset(self):
        return Activity.objects.filter(track_id=self.kwargs["track_id"]).order_by(
            "-activity_date"
        )

    def get(self, request: Request, **kwargs) -> Response:
        track_id = kwargs["track_id"]
        try:
            aggregated_data = activity_aggregator.aggregate(
                activities=self.get_queryset()
            )
            return Response(aggregated_data, HTTP_200_OK)
        except TrackIDDoesNotExists:
            return Response(
                {"message": f"Track ID {track_id} does not exists"},
                HTTP_404_NOT_FOUND,
            )
        except CannotCalculateAmount:
            return Response(
                {"message": f"Cannot calculate amount for {track_id}"},
                HTTP_400_BAD_REQUEST,
            )


activity_retrieve_view = ActivityRetrieveView.as_view()
