import tkinter as tk
from tkinter import messagebox
import re
import webbrowser
import os
import requests
from flask import Flask, request, jsonify, send_file
from threading import Thread
from get_youtube_transcript import get_transcript, update_transcript_html
from gemini_intergration import generate_summary_html
from chatbox import ChatHandler

app = Flask(__name__)


#Flask Routes
def ask_question(question):
    try:
        response = requests.post("http://127.0.0.1:5000/chat", json={"question": question})
        response.raise_for_status()
        data = response.json()
        return data.get("answer", "(No answer)")
    except Exception as e:
        print(f"Error in ask_question: {e}")
        return "(Error processing your request)"


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get("question")
    video_id = str(data.get("video_id", "")).strip()  # Ensure it's a string

    if not video_id:
        return jsonify({"answer": "Error: Missing video ID."})

    try:
        transcript = get_transcript(video_id)
    except Exception as e:
        print("Transcript fetch error:", e)
        return jsonify({"answer": f"Error fetching transcript: {e}"})

    if not transcript:
        return jsonify({"answer": "Sorry, no transcript found."})

    try:
        chat_handler = ChatHandler(transcript)
        response = chat_handler.ask(question)
        return jsonify({"answer": response})
    except Exception as e:
        print("Chat handler error:", e)
        return jsonify({"answer": "Error processing your request."})


@app.route('/video/<video_id>')
def serve_transcript(video_id):

    filename = 'smart_transcript.html'
    if not os.path.exists(filename):
        return "Transcript not found", 404
    return send_file(filename)

#Run Flask
def run_flask():
    app.run(debug=False, use_reloader=False)

#GUI to extract video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

#When user submits URL
def process_url():
    url = url_entry.get()
    video_id = extract_video_id(url)
    if not video_id:
        messagebox.showerror("Invalid URL", "Please enter a valid YouTube video URL.")
        return

    #Update transcript & generate HTML
    update_transcript_html(video_id)
    transcript = get_transcript(video_id)

    if transcript is None:
        messagebox.showerror("No Transcript", "Could not retrieve transcript.")
        return

    html = generate_summary_html(transcript, video_id)
    filename = "smart_transcript.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    #Open the transcript page served by Flask
    webbrowser.open(f"http://127.0.0.1:5000/video/{video_id}")

#GUI setup
root = tk.Tk()
root.title("Multimodal Video Analysis")
root.geometry("400x200")
root.configure(bg="#f0f8ff")

label = tk.Label(root, text="Enter YouTube Video URL:", bg="#f0f8ff", font=("Arial", 12))
label.pack(pady=20)

url_entry = tk.Entry(root, width=50)
url_entry.pack()

submit_btn = tk.Button(root, text="Submit", command=process_url, bg="#007bff", fg="white", font=("Arial", 11))
submit_btn.pack(pady=20)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    root.mainloop()
