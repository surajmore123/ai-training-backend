from collections import defaultdict
from trainer.models import MeetingTranscript
import os
import json
import hashlib
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))





TOPIC_KEYWORDS = {
    "Authentication": ["auth", "jwt", "token", "login"],
    "Deployment": ["deploy", "deployment", "production", "staging"],
    "Environment Setup": ["environment", "env", "variables", "config"],
    "Onboarding": ["new developer", "onboarding", "setup"],
    "Common Issues": ["issue", "error", "problem", "troubleshoot"]
}

def detect_topics():
    transcripts = MeetingTranscript.objects.all()
    topic_map = defaultdict(list)

    for transcript in transcripts:
        text = transcript.content.lower()

        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                topic_map[topic].append(transcript.title)

    return dict(topic_map)


BASE_OUTPUT_DIR = "output/training_modules"

ROLE_GUIDANCE = {
    "Backend Engineer": "Focus on API implementation, authentication flow, and security best practices.",
    "Frontend Engineer": "Understand integration points, token handling, and common API errors.",
    "QA Engineer": "Test edge cases, token expiry scenarios, and deployment validation."
}

def generate_training_modules():
    topics = detect_topics()
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

    for topic, meetings in topics.items():
        file_name = topic.lower().replace(" ", "_") + ".md"
        file_path = os.path.join(BASE_OUTPUT_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n")

            f.write("## Overview\n")
            f.write(
                f"This training module is generated from recurring discussions in the following meetings:\n"
            )
            for meeting in meetings:
                f.write(f"- {meeting}\n")
            f.write("\n")

            f.write("## Step-by-Step Guide\n")
            f.write("1. Understand the concept and purpose.\n")
            f.write("2. Follow documented best practices discussed in meetings.\n")
            f.write("3. Apply the steps consistently across projects.\n")
            f.write("4. Validate using common scenarios.\n\n")

            f.write("## FAQs\n")
            f.write("- What are the common mistakes?\n")
            f.write("- How can these issues be avoided?\n")
            f.write("- What should be checked during implementation?\n\n")

            f.write("## Role-Based Learning\n")
            for role, guidance in ROLE_GUIDANCE.items():
                f.write(f"### {role}\n")
                f.write(f"{guidance}\n\n")

    return "Training modules generated successfully"



VERSION_FILE = "output/versions.json"

def _hash_text(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def update_versions():
    os.makedirs("output", exist_ok=True)

    topics = detect_topics()
    current_state = {}

    # Load existing versions if present
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            previous_versions = json.load(f)
    else:
        previous_versions = {}

    for topic, meetings in topics.items():
        combined_text = topic + "".join(meetings)
        content_hash = _hash_text(combined_text)

        if topic in previous_versions:
            if previous_versions[topic]["hash"] != content_hash:
                version = round(previous_versions[topic]["version"] + 0.1, 1)
            else:
                version = previous_versions[topic]["version"]
        else:
            version = 1.0

        current_state[topic] = {
            "version": version,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_meetings": meetings,
            "hash": content_hash
        }

    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(current_state, f, indent=2)

    return "Version tracking updated successfully"

def generate_embeddings():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    transcripts = MeetingTranscript.objects.all()

    embedded_data = []

    for transcript in transcripts:
        embedding = model.encode(transcript.content)
        embedded_data.append({
            "title": transcript.title,
            "content": transcript.content,
            "embedding": embedding
        })

    return embedded_data



def cluster_topics(similarity_threshold=0.6):
    data = generate_embeddings()   # ← this must exist in SAME FILE

    embeddings = np.array([item["embedding"] for item in data])
    titles = [item["title"] for item in data]

    similarity_matrix = cosine_similarity(embeddings)

    clusters = {}
    visited = set()
    topic_id = 1

    for i in range(len(titles)):
        if i in visited:
            continue

        clusters[f"Topic_{topic_id}"] = [titles[i]]
        visited.add(i)

        for j in range(i + 1, len(titles)):
            if similarity_matrix[i][j] >= similarity_threshold:
                clusters[f"Topic_{topic_id}"].append(titles[j])
                visited.add(j)

        topic_id += 1

    return clusters


def generate_training_with_gemini():
    """
    Uses Gemini (new SDK) to generate structured training modules
    from AI-clustered meeting topics.
    """

    clusters = cluster_topics()
    ai_outputs = {}

    for topic, meetings in clusters.items():
        prompt = f"""
You are an AI assistant converting meeting discussions into training material.

Meetings:
{', '.join(meetings)}

Instructions:
- Create a clear Overview
- Provide Step-by-step guidance
- List common FAQs
- Add Role-based learning for Backend, Frontend, and QA engineers

Output in clean Markdown format.
"""

        response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
        )


        ai_outputs[topic] = response.text

    return ai_outputs



def save_gemini_training_modules():
    ai_outputs = generate_training_with_gemini()
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

    for topic, content in ai_outputs.items():
        file_name = topic.lower().replace(" ", "_") + ".md"
        file_path = os.path.join(BASE_OUTPUT_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return "Gemini training modules saved successfully"





