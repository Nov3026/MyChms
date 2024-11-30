from django.urls import path
from .import views


urlpatterns = [
   # path('api/login/', views.LoginView.as_view(), name='login'),
    path('', views.CreateChurchAccount.as_view(), name='Create'),
    path('api/church-accounts/', views.ChurchAccountList.as_view(), name='church_accounts'),
    path('api/church-account/<int:pk>/', views.ChurchAccountDetail.as_view(), name='church_account'),
    path('api/church-account-delete/<int:pk>/', views.ChurchAccountDeleteView.as_view(), name='church_account_delete'),

    # member endpoint
    path('api/create/members/', views.MemberCreateView.as_view(), name='register-member'),
    path('api/members/', views.MemberListView.as_view(), name='member-list'),
    path('api/members/<int:pk>/', views.MemberDetailView.as_view(), name='member-update-delete'),

    path('api/general-stats/', views.GeneralStatisticsView.as_view(), name='general-stats'),
    path('api/choir-stats/', views.ChoirStatsView.as_view(), name='choir-stats'),

    # Department endpoints
    path('api/create/departments/',views.DepartmentCreateView.as_view()),
    path('api/departments/',views.DepartmentListView.as_view()),
    path('api/departments/<int:pk>/',views.DepartmentDetailUpdateDeleteView.as_view()),
    
    #Choir Director account endpoints
    path('api/directors/create/', views.ChoirDirectorAccountCreateAPIView.as_view()),
    path('api/choir/directors/', views.ChoirDirectorAccountListView.as_view()),
    path('api/choir/director/<int:pk>/', views.ChoirDirectorAccountDetailAPIView.as_view()),
    path('api/choir/director/update/delete/<int:pk>/', views.ChoirDirectorAccountUpdateDeleteAPIView.as_view()),

   # Choir Member account endpoints
    path('api/create/choir-members/', views.ChoirMemberAccountCreateAPIView.as_view(), name='choir-member'),
    path('api/choir/members/', views.ChoirMemberAccountListAPIView.as_view(), name='choir-member'),
    path('api/choir/members/<int:pk>/', views.ChoirMemberAccountDetailAPIView.as_view(), name='choir-update-delete'),

   # Secretary Account endpoints
    path('api/secretary/create/', views.SecretaryAccountCreateAPIView.as_view(), name='create-secretary'),
    path('api/secretaries/', views.SecretaryAccountListView.as_view(), name='secretaries'),
    path('api/secretaries/<int:pk>/', views.SecretaryAccountDetailView.as_view(), name='secretaries'),
    path('api/delete/secretaries/<int:pk>/', views.SecretaryAccountDeleteView.as_view(), name='delete_secretaries'),
]
