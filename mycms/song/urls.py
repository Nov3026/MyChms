from django.urls import path
from .import views


urlpatterns = [
    path('api/create/songs/',views.SongCreateView.as_view()),
    path('api/songs/',views.SongListView.as_view()),
    path('api/songs/<int:pk>/',views.SongDetailUpdateDeleteView.as_view()),
]