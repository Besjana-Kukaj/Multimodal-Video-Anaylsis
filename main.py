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

#Global Chathandler Instance
global_chat_handler = None



def ask_question(question):
    try:
        response = requests.post("http://127.0.0.1:5000/chat", json={"question": question})
        response.raise_for_status()
        data = response.json()
        return data.get("answer", "(No answer)")
    except Exception as e:
        print(f"Error in ask_question (GUI wrapper): {e}")
        return "(Error processing your request)"

# Flask Routes
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get("question")
    video_id = str(data.get("video_id", "")).strip()

    if not video_id:
        return jsonify({"answer": "Error: Missing video ID."})


    if global_chat_handler is None:

        return jsonify({"answer": "Error: AI not initialized. Please restart the application."})

    response = global_chat_handler.ask_question(question, video_id, get_transcript)

    return jsonify({"answer": response})


@app.route('/video/<video_id>')
def serve_transcript(video_id):
    filename = 'smart_transcript.html'
    if not os.path.exists(filename):
        return "Transcript not found", 404
    return send_file(filename)


# Run Flask
def run_flask():
    app.run(debug=False, use_reloader=False)


# GUI to extract video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None


# When user submits URL
def process_url():
    url = url_entry.get()
    video_id = extract_video_id(url)
    if not video_id:
        messagebox.showerror("Invalid URL", "Please enter a valid YouTube video URL.")
        return

    # Update transcript file and generate HTML summary
    transcript = get_transcript(video_id)
    if transcript is None:
        messagebox.showerror("No Transcript", "Could not retrieve transcript.")
        return

    html = generate_summary_html(transcript, video_id)
    filename = "smart_transcript.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open(f"http://127.0.0.1:5000/video/{video_id}")


# GUI setup
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
    try:
        global_chat_handler = ChatHandler()
        print("Global ChatHandler (and LLM/Embedder) initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize global ChatHandler (and LLM/Embedder) at startup: {e}")
        messagebox.showerror("Initialization Error", f"Failed to load AI model: {e}\nCheck model path and resources.")
        exit()

    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    root.mainloop()