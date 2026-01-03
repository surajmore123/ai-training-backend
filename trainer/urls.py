from django.urls import path
from .views import health_check,upload_transcript, upload_transcript, process_ai,list_topics,get_training_module


urlpatterns = [
    path("health/", health_check),
    path("transcripts/", upload_transcript),
    path("process-ai/", process_ai),
    path("topics/", list_topics),
    path("module/<str:topic>/", get_training_module),
]
