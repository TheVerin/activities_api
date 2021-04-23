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

from activity.exceptions.activity_exceptions import TrackIDDoesNotExists
from activity.models import Activity
from activity.serializers import ActivityAggregateSerializer, ActivitySerializer
from activity.tools.aggregators import activity_aggregator
from activity.tools.checkers import activity_checker


class ActivityRetrieveView(APIView):
    def get_queryset(self):
        return Activity.objects.filter(track_id=self.kwargs["track_id"]).order_by(
            "-activity_date"
        )

    @swagger_auto_schema(responses={200: ActivityAggregateSerializer, 404: "Not found"})
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


activity_retrieve_view = ActivityRetrieveView.as_view()


class ActivityCreateView(APIView):

    @swagger_auto_schema(request_body=ActivitySerializer, responses={201: "Created", 400: "Bad "
                                                                                      "Request"})
    def post(self, request: Request) -> Response:
        activities = request.data
        if isinstance(activities, list):
            unique_activities = (
                activity_checker.prepare_unique_activities_possible_to_save(
                    activities=activities
                )
            )
            if len(unique_activities) == 0:
                return Response(
                    {"message": "Cannot store any activity"},
                    HTTP_400_BAD_REQUEST,
                )
            else:
                Activity.objects.bulk_create(unique_activities)
                return Response(status=HTTP_201_CREATED)
        else:
            if not activity_checker.check_possibility_to_save(data=activities):
                return Response(
                    {"message": "Cannot store any activity"},
                    HTTP_400_BAD_REQUEST,
                )
            self._perform_create(data=activities)
            return Response(status=HTTP_201_CREATED)

    def _perform_create(self, data: dict):
        serializer = ActivitySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()


activity_create_view = ActivityCreateView.as_view()
