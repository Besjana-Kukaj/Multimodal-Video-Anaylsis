from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

#Get Transcript for a video or, if not found, auto-generate
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
    except Exception as e:
        print(f"Unexpected error fetching transcript: {e}")
        return None

#Timestamp format
def format_timestamp(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

#Generate HTML with clickable timestamps
def generate_html_transcript(transcript, video_id):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>YouTube Transcript</title>
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
<h1>Transcript for Video</h1>
<div class="container">
  <div class="transcript">
"""

    for snippet in transcript:
        start = int(snippet['start'])
        time_str = format_timestamp(start)
        text = snippet['text']
        html_content += f'<div class="transcript-line"><a class="timestamp" onclick="seekTo({start})">[{time_str}]</a>{text}</div>\n'

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

  // Load YouTube IFrame Player API
  var tag = document.createElement('script');
  tag.src = "https://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
</script>

</body>
</html>
"""
    return html_content
