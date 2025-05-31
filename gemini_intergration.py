from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in environment variables. Please check your .env file.")

client = genai.Client(api_key=api_key)

#Timestamp Format
def format_timestamp(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

#Chunk the Transcript
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

#Gemini summarizes each chunk
def summarize_text(text):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Give a short 4–6 word title for this YouTube transcript segment. Be catchy, insightful, and concise. Just one title and no punctuation:\n\n{text}",
        )
        return response.text.strip().strip('"')
    except Exception as e:
        return f"(Failed to summarize: {e})"

#Main HTML
def generate_summary_html(transcript, video_id):
    chunks = chunk_transcript(transcript)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Multimodal Video Analysis</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #d0e7ff;
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
  .main-title {{
    color: #000000;
  }}
  #chatbox {{
    margin-top: 40px;
    background: #ffffff;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
  }}
  #chatlog {{
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #ccc;
    padding: 10px;
    background: #f9f9f9;
    margin-bottom: 10px;
    white-space: pre-wrap;
  }}
  #chatInput {{
    width: 80%;
    padding: 10px;
    font-size: 1em;
  }}
  #sendBtn {{
    padding: 10px 20px;
    font-size: 1em;
    margin-left: 10px;
    cursor: pointer;
  }}
</style>
</head>
<body>
<h1 class="main-title">Main Topics of the Video!</h1>
<div class="container">
  <div class="transcript">
"""
    for chunk in chunks:
        start = int(chunk["start"])
        time_str = format_timestamp(start)
        summary = summarize_text(chunk["text"])
        html_content += f'<div class="transcript-line"><a class="timestamp" onclick="seekTo({start})">[{time_str}]</a>{summary}</div>\n'
        time.sleep(0.5)

    # Video player + chat box
    html_content += f"""
  </div>
  <div class="video">
    <div id="player"></div>
    <div id="chatbox">
      <h2>Ask Questions About the Video</h2>
      <div id="chatlog"></div>
      <input type="text" id="chatInput" placeholder="Ask a question..." />
      <button id="sendBtn">Send</button>
    </div>
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

  // Chatbox functionality
  document.addEventListener("DOMContentLoaded", function() {{
    const input = document.getElementById("chatInput");
    const button = document.getElementById("sendBtn");
    const chatlog = document.getElementById("chatlog");

    button.onclick = async function() {{
      const question = input.value.trim();
      if (!question) return;

      chatlog.innerHTML += "\\nYou: " + question;
      input.value = "";

      try {{
        const res = await fetch('/ask', {{
          method: 'POST',
          headers: {{
            'Content-Type': 'application/json'
          }},
          body: JSON.stringify({{ question }})
        }});
        const data = await res.json();
        chatlog.innerHTML += "\\nAI: " + data.answer;
      }} catch (err) {{
        chatlog.innerHTML += "\\nAI: (Error processing your request)";
      }}
      chatlog.scrollTop = chatlog.scrollHeight;
    }};
  }});
</script>

</body>
</html>
"""
    return html_content

# Fetch transcript from get_youtube_transcript
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
