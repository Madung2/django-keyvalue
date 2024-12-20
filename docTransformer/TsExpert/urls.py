from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import extract_key_value, render_tsexpert, render_docGenerator, extract_term_sheet, extract
urlpatterns = [
    path('', render_tsexpert, name='render_tsexpert'),
    # path('gen/', render_docGenerator, name='render_docGenerator'),
    path('extract/', extract, name='extract'), 
    path('extract_key_value/', extract_key_value, name='extract_key_value'),
    path('extract-term-sheet/', extract_term_sheet, name='extract_term_sheet'),
    # path('extract_xl/', extract_xl, name='extract_xl'),
    # path('save_key_value/', save_key_value, name='save_key_value'),
    # path('run_generator/', run_generator, name='run_generator'),
    # path('run_generator_data/', run_generator_data, name='run_generator_data'),
    # path('task_status/<str:task_id>/', get_task_status, name='get_task_status'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
