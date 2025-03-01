import os
import re
import time
from pytube import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptAvailable

def extract_video_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    match = re.match(youtube_regex, url)
    if match:
        return match.group(6)
    return None

def get_playlist_videos(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        print(f"Playlist: {playlist.title}")
        print(f"Number of videos: {len(playlist.video_urls)}")
        
        videos = []
        for i, url in enumerate(playlist.video_urls, 1):
            videos.append({
                'drama_name': playlist.title,  # Use playlist title instead of video title
                'episode_number': str(i),
                'url': url
            })
            print(f"Found: {playlist.title} - Episode {i}")
            time.sleep(0.5)
        
        return videos
    except Exception as e:
        print(f"Error processing playlist: {str(e)}")
        return []

def get_available_languages(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = []
        translatable_languages = []
        for transcript in transcript_list:
            lang_code = transcript.language_code
            is_translatable = transcript.is_translatable
            available_languages.append(lang_code)
            if is_translatable:
                translatable_languages.append(lang_code)
        return available_languages, translatable_languages
    except Exception as e:
        print(f"Error getting transcript languages: {str(e)}")
        return [], []

def get_transcript(video_id, output_path, drama_name, episode_number, language='en'):
    try:
        available_languages, translatable_languages = get_available_languages(video_id)
        transcript = None
        lang_name = "English" if language == 'en' else "Urdu"
        used_translation = False
        
        if language in available_languages:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            print(f"Found direct {lang_name} transcript.")
        elif translatable_languages:
            source_lang = translatable_languages[0]
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            source_transcript = transcript_list.find_transcript([source_lang])
            transcript = source_transcript.translate(language).fetch()
            used_translation = True
            print(f"Using translated {lang_name} transcript (from {source_lang}).")
        else:
            print(f"No {lang_name} transcript or translation available for this video.")
            return False
        
        if transcript:
            safe_drama_name = drama_name.replace(' ', '_')
            with_timestamps_filename = f"{safe_drama_name}_Ep_{episode_number}_{lang_name}_T.txt"
            with_timestamps_path = os.path.join(output_path, with_timestamps_filename)
            
            without_timestamps_filename = f"{safe_drama_name}_Ep_{episode_number}_{lang_name}.txt"
            without_timestamps_path = os.path.join(output_path, without_timestamps_filename)
            
            with open(with_timestamps_path, 'w', encoding='utf-8') as f:
                if used_translation:
                    f.write(f"# Note: This is a translated transcript\n\n")
                for entry in transcript:
                    start_time = format_timestamp(entry['start'])
                    text = entry['text']
                    f.write(f"[{start_time}] {text}\n")
            print(f"Transcript with timestamps saved to: {with_timestamps_path}")
            
            with open(without_timestamps_path, 'w', encoding='utf-8') as f:
                if used_translation:
                    f.write(f"# Note: This is a translated transcript\n\n")
                for entry in transcript:
                    f.write(f"{entry['text']}\n")
            print(f"Transcript without timestamps saved to: {without_timestamps_path}")
            
            return True
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for {drama_name} Ep {episode_number} ({language}).")
    except NoTranscriptAvailable:
        print(f"No {lang_name} transcript is available for {drama_name} Ep {episode_number}.")
    except Exception as e:
        print(f"Error getting transcript for {drama_name} Ep {episode_number} ({language}): {str(e)}")
    return False

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def process_playlist(playlist_url, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    videos = get_playlist_videos(playlist_url)
    if not videos:
        print("No videos found in the playlist.")
        return
    
    success_count = 0
    fail_count = 0
    
    for i, video in enumerate(videos, 1):
        drama_name = video['drama_name']
        episode_number = video['episode_number']
        url = video['url']
        print(f"\n[{i}/{len(videos)}] Processing: {drama_name} - Episode {episode_number}")
        
        video_id = extract_video_id(url)
        if not video_id:
            print(f"Invalid YouTube URL: {url}")
            fail_count += 1
            continue
        
        get_transcript(video_id, output_path, drama_name, episode_number, 'en')
        get_transcript(video_id, output_path, drama_name, episode_number, 'ur')
        
        success_count += 1
        time.sleep(1)
    
    print(f"\nProcessing complete.")
    print(f"Successfully processed: {success_count} videos")
    print(f"Failed: {fail_count} videos")

def main():
    playlist_url = input("Enter YouTube playlist URL: ")
    output_path = "transcripts"
    print(f"Starting transcript extraction from playlist: {playlist_url}")
    process_playlist(playlist_url, output_path)

if __name__ == "__main__":
    main()
