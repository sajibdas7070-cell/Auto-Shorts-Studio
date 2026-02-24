import os, random, subprocess, sys, pickle, time
from googlesearch import search
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- ১. ফাইল চেক (তোমার ঠিক করা নামের জন্য) ---
TOKEN_FILE = "token.pickle"

if not os.path.exists(TOKEN_FILE):
    print(f"❌ এরর: '{TOKEN_FILE}' ফাইলটি পাওয়া যাচ্ছে না!")
    sys.exit(1)

print(f"✅ ফাইল লোড হয়েছে: {TOKEN_FILE}")

# --- ২. সেফ ভিডিও খোঁজা (ব্লক বাইপাস সিস্টেম) ---
def find_video_via_google():
    print("🔍 ভিডিও খোঁজা হচ্ছে (Google Method)...")
    queries = [
        "site:youtube.com viral russian movie trailer 2024",
        "site:youtube.com best polish thriller movie clip",
        "site:youtube.com chinese sci-fi movie scenes viral"
    ]
    query = random.choice(queries)
    
    try:
        # ইউটিউব সার্চ না করে গুগল থেকে লিংক নেওয়া হচ্ছে (ব্লক হবে না)
        links = list(search(query, num_results=10, lang="en"))
        
        # ফিল্টার: শুধু ইউটিউব ভিডিও লিংক নেওয়া
        youtube_links = [link for link in links if "watch?v=" in link]
        
        if not youtube_links:
            print("⚠️ কোনো ভিডিও পাওয়া যায়নি।")
            return None
            
        video_url = random.choice(youtube_links)
        print(f"🎯 টার্গেট ভিডিও: {video_url}")
        
        # ভিডিওর টাইটেল বের করা
        cmd = f'yt-dlp --get-title "{video_url}" --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'
        title = subprocess.check_output(cmd, shell=True).decode().strip()
        return {"title": title, "url": video_url}
        
    except Exception as e:
        print(f"❌ সার্চ এরর: {e}")
        return None

# --- ৩. ডাউনলোড ও এডিটিং ---
def process_video(video_data):
    print(f"⬇️ ডাউনলোড হচ্ছে: {video_data['title']}")
    
    # স্পেশাল কমান্ড: ইউটিউবকে মোবাইল ফোন হিসেবে পরিচয় দেওয়া (Android Client)
    cmd = [
        'yt-dlp', 
        '-f', 'bestvideo[height<=720]+bestaudio/best', 
        '-o', 'raw.mp4', 
        '--no-check-certificate',
        '--extractor-args', 'youtube:player_client=android', # মোবাইল ট্রিক
        '--user-agent', 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        video_data['url']
    ]
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("❌ ডাউনলোড ফেইল করেছে! অন্য ভিডিও ট্রাই করা উচিত।")
        sys.exit(1)

    print("🎬 এডিটিং চলছে...")
    # মিরর + জুম (কপিরাইট বাইপাস)
    edit_cmd = [
        'ffmpeg', '-y', '-i', 'raw.mp4',
        '-vf', "hflip,scale=1280:720,eq=brightness=0.05:contrast=1.1,zoompan=z='min(zoom+0.001,1.1)':d=1:s=1280x720",
        '-af', "asetrate=44100*0.98,atempo=1.02",
        '-t', '59', 'final.mp4'
    ]
    subprocess.run(edit_cmd)

# --- ৪. আপলোড ---
def upload_video(title):
    print("🚀 আপলোড হচ্ছে...")
    try:
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
        
        youtube = build("youtube", "v3", credentials=creds)
        
        body = {
            "snippet": {
                "title": f"{title[:50]}... - Movie Explained 🎬 #shorts",
                "description": "Viral movie clip explained. #shorts #viral #movie",
                "categoryId": "24"
            },
            "status": {"privacyStatus": "public"}
        }
        
        youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload("final.mp4", resumable=True)
        ).execute()
        print("💎 ভিডিও সাকসেসফুলি পোস্ট হয়েছে!")
        
    except Exception as e:
        print(f"❌ আপলোড এরর: {e}")
        sys.exit(1)

if __name__ == "__main__":
    video = find_video_via_google()
    if video:
        process_video(video)
        upload_video(video['title'])
    else:
        print("ভিডিও পাওয়া যায়নি, আবার চেষ্টা করো।")
        sys.exit(1)
        
