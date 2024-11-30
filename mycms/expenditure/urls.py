from django.urls import path
from .import views


urlpatterns = [
    path('api/create/expenditures/',views.ExpenditureCreateView.as_view()),
    path('api/expenditures/',views.ExpenditureListView.as_view()),
    path('api/expenditures/<int:pk>/',views.ExpenditureDetailUpdateDeleteView.as_view()),
]