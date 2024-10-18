from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import * 
urlpatterns = [
    # path('', render_tsexpert, name='render_tsexpert'),
    # path('gen/', render_docGenerator, name='render_docGenerator'),
    # path('extract_key_value/', extract_key_value, name='extract_key_value'),
    # path('extract_xl/', extract_xl, name='extract_xl'),
    # path('save_key_value/', save_key_value, name='save_key_value'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


