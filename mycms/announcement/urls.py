from django.urls import path
from .import views


urlpatterns = [
    path('api/create/announcements/',views.AnnouncementCreateView.as_view()),
    path('api/announcements/',views.AnnouncementListView.as_view()),
    path('api/announcements/<int:pk>/',views.AnnouncementDetailUpdateDeleteView.as_view()),

    path('api/announcement-stats/',views.AnnounceStatsView.as_view()),
]