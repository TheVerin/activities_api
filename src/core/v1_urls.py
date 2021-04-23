from typing import List

from django.urls import include, path


urlpatterns: List[path] = [path("activity/", include("activity.urls"))]
