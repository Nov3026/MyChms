from django.urls import path
from . import views

urlpatterns = [
    path('api/create/choir-dues/', views.ChoirDueCreateAPIView.as_view(), name='add_choir_due'),
    path('api/choir-dues/', views.ChoirDueListAPIView.as_view(), name='choir_due_list'),
    path('api/choir-dues/<int:pk>/', views.ChoirDueDetailUpdateDeleteAPIView.as_view(), name='choir_due'),
]
