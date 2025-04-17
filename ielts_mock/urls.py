from django.urls import path
from . import views

urlpatterns = [
    path('', views.mock_test_home, name='mock_test_home'),
    path('start-test/', views.start_test, name='start_test'),
    path('reading-test/<uuid:test_id>/', views.reading_test, name='reading_test'),
    path('listening-test/<uuid:test_id>/', views.listening_test, name='listening_test'),
    path('writing-test/<uuid:test_id>/', views.writing_test, name='writing_test'),
    path('submit-reading/<uuid:test_id>/', views.submit_reading, name='submit_reading'),
    path('submit-listening/<uuid:test_id>/', views.submit_listening, name='submit_listening'),
    path('submit-writing/<uuid:test_id>/', views.submit_writing, name='submit_writing'),
    path('results/<uuid:test_id>/', views.test_results, name='test_results'),
    path('results/<uuid:test_id>/download/', views.download_results, name='download_results'),
    # path('results/<uuid:test_id>/share/', views.share_results, name='share_results'),
    path('analysis/<uuid:test_id>/<str:section>/', views.section_analysis, name='section_analysis'),
    path('writing-analysis/<uuid:test_id>/', views.writing_analysis, name='writing_analysis'),
    path('improvement-plan/<uuid:test_id>/', views.improvement_plan, name='improvement_plan'),
    path('audio/<uuid:test_id>/<int:section_number>/', views.get_listening_audio, name='get_listening_audio'),
    # History features
    path('history/', views.test_history, name='test_history'),
    path('history/comparison/', views.test_comparison, name='test_comparison'),
    path('history/progress/', views.progress_overview, name='progress_overview'),
    # New writing practice section
    # path('writing-practice/', views.writing_practice, name='writing_practice'),
    # path('writing-practice/submit/', views.submit_writing_practice, name='submit_writing_practice'),
    # path('writing-practice/results/<uuid:practice_id>/', views.writing_practice_results, name='writing_practice_results'),
]
