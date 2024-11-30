from django.urls import path
from .import views


urlpatterns = [
    path('api/create/activity/',views.ChurchActivityCreateView.as_view()),
    path('api/activities/',views.ChurchActivityListView.as_view()),
    path('api/update/delete/activity/<int:pk>/',views.ChurchActivityDetailUpdateDeleteView.as_view()),
]