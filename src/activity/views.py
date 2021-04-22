from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from activity.exceptions.activity_exceptions import (
    CannotCalculateAmount,
    TrackIDDoesNotExists,
)
from activity.models import Activity
from activity.serializers import ActivityAggregateSerializer, ActivitySerializer
from activity.tools.aggregators import activity_aggregator


class ActivityRetrieveView(APIView):
    def get_queryset(self):
        return Activity.objects.filter(track_id=self.kwargs["track_id"]).order_by(
            "-activity_date"
        )

    @swagger_auto_schema(responses={200: ActivityAggregateSerializer})
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


class ActivityCreateView(CreateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        activities = request.data
        if isinstance(activities, list):
            output_data = [
                self._perform_create(data=activity)
                for activity in activities
                if not Activity.objects.filter(id=activity["id"]).exists()
            ]
            if len(output_data) == 0:
                return Response(
                    {"message": "All activities are already in db"},
                    HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(output_data, HTTP_201_CREATED)
        else:
            if Activity.objects.filter(id=activities["id"]).exists():
                return Response(
                    {"message": f"Activity {activities['id']} already in db"},
                    HTTP_400_BAD_REQUEST,
                )
            output_data = [self._perform_create(data=activities)]
            return Response(output_data, HTTP_201_CREATED)

    def _perform_create(self, data: dict) -> dict:
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data


activity_create_view = ActivityCreateView.as_view()
