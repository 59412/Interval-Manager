from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:duration>/<str:webhook_url>/', views.create_interval_request_handler),
    path('check/<str:interval_id>/', views.check_status_request_handler),
    path('pause/<str:interval_id>/', views.pause_interval_request_handler),
    path('resume/<str:interval_id>/', views.resume_interval_request_handler),
]
