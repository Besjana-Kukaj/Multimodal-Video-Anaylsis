from youtube_transcript_api import YouTubeTranscriptApi

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

video_id = 'Ks-_Mh1QhMc'
transcript = YouTubeTranscriptApi.get_transcript(video_id)

for snippet in transcript:
    time_str = format_timestamp(snippet['start'])
    print(f"{time_str} - {snippet['text']}")