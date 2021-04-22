from typing import List

from django.urls import path

from activity.views import activity_retrieve_view


urlpatterns: List[path] = [
    path("<str:track_id>/", activity_retrieve_view, name="activity_aggregate")
]
