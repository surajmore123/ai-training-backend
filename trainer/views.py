from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import MeetingTranscriptSerializer
from .models import MeetingTranscript
from .utility import save_gemini_training_modules, update_versions
import json
import os

@api_view(['GET'])
def health_check(request):
    return Response({"status": "API is working"})



@api_view(['POST'])
def upload_transcript(request):
    title = request.data.get("title")
    content = request.data.get("content")
    file = request.FILES.get("file")

    if not title:
        return Response(
            {"error": "Title is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Case 1: File upload
    if file:
        try:
            text = file.read().decode("utf-8")
        except Exception:
            return Response(
                {"error": "Unable to read uploaded file"},
                status=status.HTTP_400_BAD_REQUEST
            )

        MeetingTranscript.objects.create(
            title=title,
            content=text
        )

        return Response(
            {"message": "File uploaded and processed successfully"},
            status=status.HTTP_201_CREATED
        )

    # Case 2: Text upload
    if content:
        MeetingTranscript.objects.create(
            title=title,
            content=content
        )

        return Response(
            {"message": "Text transcript uploaded successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(
        {"error": "Provide either text content or a file"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def process_ai(request):
    """
    Triggers the full AI pipeline:
    - Embeddings
    - Clustering
    - Gemini generation
    - Markdown saving
    - Version tracking
    """
    try:
        save_gemini_training_modules()
        update_versions()

        return Response(
            {"message": "AI processing completed successfully"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def list_topics(request):
    """
    Returns all available topics with version info.
    """
    try:
        with open("output/versions.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        topics = []
        for topic, info in data.items():
            topics.append({
                "topic": topic,
                "version": info["version"],
                "last_updated": info["last_updated"],
                "source_meetings": info["source_meetings"],
            })

        return Response(topics, status=status.HTTP_200_OK)

    except FileNotFoundError:
        return Response(
            {"error": "No topics found. Run AI processing first."},
            status=status.HTTP_404_NOT_FOUND
        )
    
@api_view(['GET'])
def get_training_module(request, topic):
    """
    Returns Markdown content for a specific topic.
    """
    file_name = topic.lower().replace(" ", "_") + ".md"
    file_path = os.path.join("output/training_modules", file_name)

    if not os.path.exists(file_path):
        return Response(
            {"error": "Training module not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return Response(
        {
            "topic": topic,
            "content": content
        },
        status=status.HTTP_200_OK
    )
