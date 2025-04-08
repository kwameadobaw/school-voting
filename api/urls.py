from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('voting/', views.voting, name='voting'),
    path('get_candidates/', views.get_candidates, name='get_candidates'),
    path('submit_vote/', views.submit_vote, name='submit_vote'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout, name='logout'),
]

# Add this to serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
