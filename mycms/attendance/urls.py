from django.urls import path
from .import views


urlpatterns = [
    #church attendance endpoint
    path('api/create/church/attendance/',views.ChurchserviceAttendanceCreateView.as_view()),
    path('api/church/attendance/',views.ChurchserviceAttendanceListView.as_view()),
    path('api/update/delete/church/attendance/<int:pk>/',views.ChurchserviceAttendanceDetailUpdateDeleteView.as_view()),

    #choir practice attendance endpoint
    path('api/create/choir/attendance/',views.ChoirAttendanceCreateView.as_view()),
    path('api/choir/attendance/',views.ChoirAttendanceListView.as_view()),
    path('api/update/delete/choir/attendance/<int:pk>/',views.ChoirAttendanceDetailUpdateDeleteView.as_view()),
]