from flask import Flask, render_template, request, send_file, redirect, url_for
import requests
from bs4 import BeautifulSoup
import os
import re
import pyktok
import uuid

app = Flask(__name__)

# Fungsi untuk mendownload video TikTok
def download_tiktok_video(url):
    try:
        # Menggunakan pyktok untuk mendapatkan metadata video
        pyktok.specify_browser('chrome')
        video_metadata = pyktok.get_video_metadata(url)
        
        if video_metadata:
            video_url = video_metadata['video_url']
            video_id = str(uuid.uuid4())
            video_path = f"downloads/{video_id}.mp4"
            
            # Membuat folder downloads jika belum ada
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            
            # Download video
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                return video_path, None
            else:
                return None, "Gagal mengunduh video"
        else:
            return None, "Tidak dapat mengambil metadata video"
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return redirect(url_for('index'))
    
    # Validasi URL TikTok
    if not re.match(r'https?://(www\.)?tiktok\.com/.+', url):
        return render_template('index.html', error="URL TikTok tidak valid")
    
    video_path, error = download_tiktok_video(url)
    
    if error:
        return render_template('index.html', error=error)
    
    return send_file(video_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)