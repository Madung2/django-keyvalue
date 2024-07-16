from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import extract_key_value, extract_xl
urlpatterns = [
    path('extract_key_value/', extract_key_value, name='extract_key_value'),
    path('extract_xl/', extract_xl, name='extract_xl'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)