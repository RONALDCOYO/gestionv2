from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registro/inicio de sesión.html'), name='login'),
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')),  # Incluir las URLs de la app 'gestion'
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   
]
# Añadir las URLs para los archivos multimedia (documentos subidos)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
