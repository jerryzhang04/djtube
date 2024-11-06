from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL
from moviepy.editor import *
import openai
import os
import tempfile

from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file
openai.api_key = os.getenv('OPENAI_API_KEY')




app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to get song information using ChatGPT and analyze audio
@app.route('/get_information', methods=['POST'])
def get_information():
    youtube_url = request.form['youtube_url']
    temp_dir = tempfile.gettempdir()
    download_path = os.path.join(temp_dir, "youtube_audio.mp4")
    try:
        # Use OpenAI API to get song information with the new version
        prompt = f"Provide the name, BPM, key, and length of the song in this YouTube link: {youtube_url}."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        song_info = response['choices'][0]['message']['content'].strip()

        # Step 1: Download audio using yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': download_path,
            'quiet': False,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Step 2: Get audio length using moviepy
        video = AudioFileClip(download_path)
        song_length = video.duration
        video.close()

        # Render the information on the page
        return render_template('index.html', youtube_url=youtube_url, song_info=song_info, song_length=song_length)

    except openai.error.OpenAIError as e:
        return f"Error: Unable to retrieve song information. {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Cleanup downloaded files
        if os.path.exists(download_path):
            os.remove(download_path)



# Route to handle conversion and download
@app.route('/convert', methods=['POST'])
def convert():
    youtube_url = request.form['youtube_url']
    temp_dir = tempfile.gettempdir()
    download_path = os.path.join(temp_dir, "youtube_audio.mp4")
    mp3_file_path = os.path.join(temp_dir, "youtube_audio.mp3")

    try:
        # Step 1: Download audio using yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': download_path,
            'quiet': False,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Step 2: Convert video to mp3 using moviepy
        video = None
        try:
            video = AudioFileClip(download_path)
            video.write_audiofile(mp3_file_path)
        finally:
            if video:
                video.close()

        # Step 3: Provide mp3 file for download
        return send_file(mp3_file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Cleanup downloaded files after sending the mp3 file
        if os.path.exists(download_path):
            os.remove(download_path)
        if os.path.exists(mp3_file_path):
            try:
                os.remove(mp3_file_path)
            except PermissionError:
                # Handle the case where the file is still being used
                pass

if __name__ == '__main__':
    app.run(debug=True)
