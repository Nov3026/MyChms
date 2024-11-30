from django.urls import path
from .import views


urlpatterns = [
    path('api/create/tithe/',views.TitheCreateView.as_view()),
    path('api/tithes/',views.TitheListView.as_view()),
    path('api/tithes/<int:pk>/',views.TitheDetailUpdateDeleteView.as_view()),
]