import os, random, subprocess, json, asyncio, pickle, time, sys
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# কনফিগারেশন
GEMINI_KEY = os.getenv("GEMINI_KEY")

# ১. ভাইরাল মুভি খোঁজা (Bot Detection Bypass সহ)
def search_viral_content():
    queries = [
        "best russian action movie scenes 2025",
        "viral polish thriller movie clips",
        "sci-fi short film award winning full"
    ]
    query = random.choice(queries)
    print(f"🔍 Searching for: {query}")
    
    # এই কমান্ডটি ইউটিউবকে ধোঁকা দেবে যে এটি একটি সাধারণ ব্রাউজার
    cmd = [
        'yt-dlp', 
        f'ytsearch5:{query}', 
        '--get-id', '--get-title',
        '--match-filter', 'duration > 600',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    try:
        output = subprocess.check_output(cmd).decode().strip().split('\n')
        if not output: return None
        
        # র্যান্ডম একটি ভিডিও সিলেক্ট করা
        idx = random.randrange(0, len(output)-1, 2)
        return {"title": output[idx], "url": f"https://youtube.com/watch?v={output[idx+1]}"}
    except Exception as e:
        print(f"❌ Search Error: {e}")
        return None

# ২. ভিডিও ডাউনলোড ও প্রসেসিং
def process_video(data):
    print(f"⬇️ Downloading: {data['title']}")
    # ডাউনলোড কমান্ড (কুকিজ ছাড়া যাতে কাজ করে)
    cmd = [
        'yt-dlp', '-f', 'bestvideo[height<=720]+bestaudio/best', 
        '-o', 'raw.mp4', 
        '--no-check-certificate', 
        '--geo-bypass',
        data['url']
    ]
    subprocess.run(cmd)

    # ৩. এডিটিং (কপিরাইট বাইপাস)
    print("🎬 Editing video...")
    edit_cmd = [
        'ffmpeg', '-y', '-i', 'raw.mp4',
        '-vf', "hflip,scale=1280:720,eq=brightness=0.05:contrast=1.2",
        '-af', "asetrate=44100*0.98,atempo=1.02",
        '-t', '600', 'final.mp4'
    ]
    subprocess.run(edit_cmd)

# ৪. ইউটিউবে আপলোড
def upload_to_youtube(title):
    print("🚀 Uploading to YouTube...")
    if not os.path.exists("token.pickle"):
        print("❌ Error: token.pickle not found! Rename 'token (3).pickle' to 'token.pickle'")
        return

    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
    
    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": f"{title} - Hindi Explained",
            "description": "Viral movie explained in Hindi. #shorts #movie #explanation",
            "categoryId": "24"
        },
        "status": {"privacyStatus": "public"}
    }
    
    try:
        youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload("final.mp4", resumable=True)
        ).execute()
        print("✅ Upload Successful!")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

# মেইন ফাংশন
if __name__ == "__main__":
    video = search_viral_content()
    if video:
        process_video(video)
        upload_to_youtube(video['title'])
    else:
        print("⚠️ No video found today.")
        
