html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Multimodal Video Analysis</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    margin: 0;
    background-color: #ffe4ec; 
    display: flex;
    justify-content: center;
    padding: 20px;
  }}
  .wrapper {{
    display: flex;
    gap: 20px;
    max-width: 1200px;
    width: 100%;
  }}

  .main-topics {{
    flex: 0 0 400px;
    background: #ffcce1;
    padding: 15px;
    border-radius: 12px;
    height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    font-size: 0.9em;
    color: #660029;
  }}

  .main-topics h2 {{
    margin-top: 0;
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 12px;
  }}

  .topic-line {{
    margin-bottom: 25px;
  }}

  .main-topics a.timestamp {{
    color: #007bff;
    text-decoration: none;
    cursor: pointer;
    margin-right: 8px;
    font-weight: bold;
  }}

  .main-topics a.timestamp:hover {{
    text-decoration: underline;
  }}

  .main-video {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  #player {{
    width: 100%;
    max-width: 720px;
    height: 405px; /* 16:9 ratio */
    border-radius: 15px;
    box-shadow: 0 6px 15px rgba(136,0,61,0.3);
    background: black;
  }}
  #chatbox {{
    margin-top: 20px;
    background: #ffd6e8; /* lighter pink */
    padding: 15px;
    border-radius: 15px;
    width: 100%;
    max-width: 720px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  }}
  #chatbox h2 {{
    margin-top: 0;
    color: #660029;
  }}
  #chatlog {{
    max-height: 250px;
    overflow-y: auto;
    border: 1px solid #ffcce1;
    padding: 10px;
    background: #fff0f6;
    margin-bottom: 10px;
    white-space: pre-wrap;
    border-radius: 8px;
  }}
  #chatInput {{
    width: 75%;
    padding: 10px;
    font-size: 1em;
    border: 1px solid #ffcce1;
    border-radius: 8px;
    outline: none;
  }}
  #sendBtn {{
    padding: 10px 20px;
    font-size: 1em;
    margin-left: 10px;
    background-color: #ff85a2;
    border: none;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }}
  #sendBtn:hover {{
    background-color: #ff4d73;
  }}
</style>
</head>
<body>

<div class="wrapper">
  <div class="main-topics">
    <h2>Main Topics</h2>
    {transcript_lines}
  </div>

  <div class="main-video">
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
      height: '405',
      width: '720',
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
