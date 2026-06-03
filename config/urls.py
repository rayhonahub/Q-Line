from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/orgs/', include('organizations.urls')),
    path('api/queues/', include('queues.urls')),
    path('api/schema/', SpectacularAPIView.as_view(),     name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'),   name='redoc'),    
]


from django.contrib import admin
from django.conf import settings


admin.site.site_header = "Q-Line"
admin.site.site_title  = "Q-Line Admin"
admin.site.index_title = "Хуш омадед ба Q-Line!"