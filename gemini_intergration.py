from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from google import genai
from dotenv import load_dotenv
import webbrowser
import os
import time

# Load .env
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in environment variables. Please check your .env file.")
client = genai.Client(api_key=api_key)

video_id = "M3fYkEjq0hc"
youtube_base_url = f"https://www.youtube.com/watch?v={video_id}"

# Format timestamp helper
def format_timestamp(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

# Chunk transcript into ~60s blocks
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

# Use Gemini to generate summary of each chunk
def summarize_text(text):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Give a short 4–6 word title for this YouTube transcript segment. Be catchy, insightful, and concise. Just one title and no punctuation:\n\n{text}",
        )
        return response.text.strip().strip('"')  # Remove quotes if Gemini adds them
    except Exception as e:
        return f"(Failed to summarize: {e})"


# HTML generator
def generate_html_summaries(chunks, video_id):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Smart Timestamps</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    margin: 20px;
  }}
  .container {{
    display: flex;
    gap: 20px;
  }}
  .transcript {{
    flex: 1;
    overflow-y: auto;
    max-height: 90vh;
  }}
  .video {{
    flex: 1;
  }}
  a.timestamp {{
    color: #007bff;
    text-decoration: none;
    margin-right: 8px;
    cursor: pointer;
  }}
  a.timestamp:hover {{
    text-decoration: underline;
  }}
  .transcript-line {{
    margin-bottom: 10px;
  }}
</style>
</head>
<body>
<h1>Smart Transcript Summary</h1>
<div class="container">
  <div class="transcript">
"""

    for chunk in chunks:
        start = int(chunk["start"])
        time_str = format_timestamp(start)
        summary = summarize_text(chunk["text"])
        html_content += f'<div class="transcript-line"><a class="timestamp" onclick="seekTo({start})">[{time_str}]</a>{summary}</div>\n'
        time.sleep(0.5)  # Be kind to Gemini API

    html_content += f"""
  </div>
  <div class="video">
    <div id="player"></div>
  </div>
</div>

<script>
  var player;

  function onYouTubeIframeAPIReady() {{
    player = new YT.Player('player', {{
      height: '315',
      width: '560',
      videoId: '{video_id}',
      playerVars: {{
        'playsinline': 1
      }}
    }});
  }}

  function seekTo(seconds) {{
    if (player && player.seekTo) {{
      player.seekTo(seconds, true);
    }}
  }}

  var tag = document.createElement('script');
  tag.src = "https://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
</script>

</body>
</html>
"""
    return html_content


# Fetch and process transcript
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
except NoTranscriptFound:
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
except TranscriptsDisabled:
    print("Transcripts are disabled for this video.")
    transcript = None

if transcript:
    chunks = chunk_transcript(transcript)
    html_transcript = generate_html_summaries(chunks, video_id)

    with open("smart_transcript.html", "w", encoding="utf-8") as f:
        f.write(html_transcript)

    print("Smart transcript saved as smart_transcript.html.")
    webbrowser.open(f"file://{os.path.abspath('smart_transcript.html')}")
else:
    print("No transcript could be retrieved.")
