from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('announcement/', include(('announcement.urls', 'announcement'), namespace='announcement')),
    path('activity/', include(('church_activity.urls', 'church_activity'), namespace='activity')),
    path('tithe/', include(('tithe.urls', 'tithe'), namespace='tithe')),
    path('due/', include(('due.urls', 'due'), namespace='due')),
    path('song/', include(('song.urls', 'song'), namespace='song')),
    path('expenditure/', include(('expenditure.urls', 'expenditure'), namespace='expenditures')),
    path('attendance/', include(('attendance.urls', 'attendance'), namespace='attendance')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)