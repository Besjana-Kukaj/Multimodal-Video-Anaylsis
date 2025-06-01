from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in environment variables. Please check your .env file.")

client = genai.Client(api_key=api_key)

def format_timestamp(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

def chunk_transcript(transcript, chunk_duration=60):
    chunks = []
    current_chunk = {"start": transcript[0]["start"], "text": ""}
    end_time = transcript[0]["start"] + chunk_duration

    for entry in transcript:
        if entry["start"] < end_time:
            current_chunk["text"] += " " + entry["text"]
        else:
            chunks.append(current_chunk)
            current_chunk = {"start": entry["start"], "text": entry["text"]}
            end_time = entry["start"] + chunk_duration
    chunks.append(current_chunk)
    return chunks

def summarize_text(text):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Give a short 4–6 word title for this YouTube transcript segment. Be catchy, insightful, and concise. Just one title and no punctuation:\n\n{text}",
        )
        return response.text.strip().strip('"')
    except Exception as e:
        return f"(Failed to summarize: {e})"

def get_transcript(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except NoTranscriptFound:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except:
            return None
    except TranscriptsDisabled:
        return None

def generate_summary_html(transcript, video_id):
    from html_template import html_template
    chunks = chunk_transcript(transcript)
    transcript_lines = ""
    for chunk in chunks:
        start = int(chunk["start"])
        time_str = format_timestamp(start)
        summary = summarize_text(chunk["text"])
        transcript_lines += f'<div class="transcript-line"><a class="timestamp" onclick="seekTo({start})">[{time_str}]</a>{summary}</div>\n'
    return html_template.format(video_id=video_id, transcript_lines=transcript_lines)
