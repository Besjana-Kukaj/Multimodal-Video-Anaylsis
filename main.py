import tkinter as tk
from tkinter import messagebox
import re
import webbrowser
import os
from get_youtube_transcript import get_transcript
from gemini_intergration import generate_summary_html

#Get VideoID from User
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

#Run when given URL
def process_url():
    url = url_entry.get()
    video_id = extract_video_id(url)
    if not video_id:
        messagebox.showerror("Invalid URL", "Please enter a valid YouTube video URL.")
        return

    transcript = get_transcript(video_id)
    if transcript is None:
        messagebox.showerror("No Transcript", "Could not retrieve transcript.")
        return

    html = generate_summary_html(transcript, video_id)
    filename = "smart_transcript.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open(f"file://{os.path.abspath(filename)}")

#GUI
root = tk.Tk()
root.title("Multimodal Video Anaylsis")
root.geometry("400x200")
root.configure(bg="#f0f8ff")

label = tk.Label(root, text="Enter YouTube Video URL:", bg="#f0f8ff", font=("Arial", 12))
label.pack(pady=20)

url_entry = tk.Entry(root, width=50)
url_entry.pack()

submit_btn = tk.Button(root, text="Submit", command=process_url, bg="#007bff", fg="white", font=("Arial", 11))
submit_btn.pack(pady=20)

root.mainloop()
