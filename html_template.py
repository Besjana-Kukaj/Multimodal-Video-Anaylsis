html_template = """<!DOCTYPE html>
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
    {transcript_lines}
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
