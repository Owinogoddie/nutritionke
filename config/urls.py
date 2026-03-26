from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.login_view, name='landing'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('nutrition/', include('apps.nutrition.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)