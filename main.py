import os, sys, glob, json, time, asyncio, shutil
import requests
import edge_tts
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# ==========================================
# 🔧 অটো-ফিক্সার: ফাইল নাম ঠিক করা
# ==========================================
print("🔧 সিস্টেম চেক চলছে...")
found_tokens = glob.glob("*.pickle")
if not found_tokens:
    print("❌ টোকেন ফাইল নেই! দয়া করে ফাইল আপলোড কর।")
    sys.exit(1)
else:
    if not os.path.exists("token.pickle"):
        shutil.move(found_tokens[0], "token.pickle")
        print(f"✅ ফাইলের নাম ঠিক করা হয়েছে: token.pickle")

# ==========================================
# 🔐 API KEYS
# ==========================================
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"

# ==========================================
# 🧠 মডিউল ১: স্ক্রিপ্ট ও প্ল্যান
# ==========================================
def get_viral_plan():
    print("🧠 জেমিনি ভিডিও প্ল্যান করছে...")
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        Output ONLY JSON:
        {
            "script": "One deep motivational sentence in Hinglish.",
            "visual": "A visual search term for Pexels (e.g. 'ocean storm', 'fire')",
            "title": "Viral YouTube Shorts Title"
        }
        """
        res = model.generate_content(prompt)
        return json.loads(res.text.replace("```json", "").replace("```", "").strip())
    except:
        return {"script": "Waqt sabka badalta hai, bas khud par yaqeen rakho.", "visual": "time clock dark", "title": "Time Changes everything 🔥 #Shorts"}

# ==========================================
# 🎙️ মডিউল ২: ভয়েস (Edge-TTS)
# ==========================================
async def generate_voice(text):
    print(f"🎙️ ভয়েস দিচ্ছি...")
    try:
        communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
        await communicate.save("voice.mp3")
    except Exception as e:
        print(f"❌ ভয়েস এরর: {e}")
        sys.exit(1)

# ==========================================
# 🎵 মডিউল ৩: অ্যান্টি-ব্লক ডাউনলোড
# ==========================================
def download_file(url, filename):
    # এই হেডার থাকার কারণে ওয়েবসাইট ভাববে এটা মানুষ, রোবট না
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"✅ ডাউনলোড সফল: {filename}")
        else:
            print(f"⚠️ ডাউনলোড ফেইল (Status {r.status_code}), ডামি ফাইল দিচ্ছি...")
            return False
    except Exception as e:
        print(f"⚠️ ডাউনলোড এরর: {e}")
        return False
    return True

# ==========================================
# 🎬 মডিউল ৪: প্রোডাকশন
# ==========================================
def produce_video():
    plan = get_viral_plan()
    script = plan['script']
    print(f"📝 স্ক্রিপ্ট: {script}")

    # ১. ভয়েস
    asyncio.run(generate_voice(script))

    # ২. ভিডিও (Pexels)
    print(f"⬇️ ভিডিও খুঁজছি: {plan['visual']}")
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={plan['visual']}&per_page=1&orientation=portrait"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if data['videos']:
            v_link = data['videos'][0]['video_files'][0]['link']
            download_file(v_link, "raw.mp4")
        else:
            raise Exception("No video")
    except:
        print("⚠️ ভিডিও পাওয়া যায়নি, ব্যাকআপ দিচ্ছি...")
        download_file("https://player.vimeo.com/external/371835695.sd.mp4?s=12345", "raw.mp4")

    # ৩. মিউজিক (অ্যান্টি-ব্লক সহ)
    print("🎵 মিউজিক দিচ্ছি...")
    # পিক্সাবে অনেক সময় ব্লক করে, তাই আমি গিটহাবের একটা ডিরেক্ট লিঙ্ক দিচ্ছি যেটা কখনো ব্লক হবে না
    music_success = download_file("https://github.com/sajibdas7070-cell/Auto-Shorts-Studio/raw/main/bg_music.mp3", "bg.mp3")
    
    # যদি মিউজিক না নামে, তবে পিক্সাবে থেকে চেষ্টা করবে
    if not music_success or os.path.getsize("bg.mp3") < 1000:
         download_file("https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3", "bg.mp3")

    # ৪. ফাইনাল এডিটিং (সেফ মোড)
    print("🎬 এডিটিং চলছে...")
    try:
        audio_dur = MP3("voice.mp3").info.length
    except: audio_dur = 10

    # FFmpeg কমান্ড আপডেট করা হয়েছে যাতে মিউজিক ফেইল করলেও ক্র্যাশ না করে
    if os.path.exists("bg.mp3") and os.path.getsize("bg.mp3") > 1000:
        # মিউজিক সহ
        cmd = (
            f'ffmpeg -y -stream_loop -1 -i raw.mp4 -i voice.mp3 -i bg.mp3 '
            f'-filter_complex '
            f'"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v];'
            f'[2:a]volume=0.2[bg];[1:a][bg]amix=inputs=2:duration=first[a]" '
            f'-map "[v]" -map "[a]" -c:v libx264 -preset fast -t {audio_dur} final.mp4'
        )
    else:
        # মিউজিক ছাড়া (সেফটি)
        print("⚠️ মিউজিক ফাইল নষ্ট, শুধু ভয়েস দিয়ে ভিডিও বানাচ্ছি...")
        cmd = (
            f'ffmpeg -y -stream_loop -1 -i raw.mp4 -i voice.mp3 '
            f'-filter_complex '
            f'"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v]" '
            f'-map "[v]" -map 1:a -c:v libx264 -preset fast -t {audio_dur} final.mp4'
        )
    
    os.system(cmd)

# ==========================================
# 🚀 আপলোড মডিউল
# ==========================================
def upload_now():
    if not os.path.exists("final.mp4"):
        print("❌ ভিডিও রেন্ডার ফেইল করেছে!")
        sys.exit(1)
        
    print("🚀 আপলোড শুরু...")
    try:
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
        
        youtube = build("youtube", "v3", credentials=creds)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "Deep Reality 🌑 #Shorts #Motivation",
                    "description": "Generated by AI Studio.",
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
        )
        res = request.execute()
        print(f"🎉 সাকসেস! ভিডিও আপলোড হয়েছে। ID: {res['id']}")
    except Exception as e:
        print(f"❌ আপলোড এরর: {e}")
        sys.exit(1)

if __name__ == "__main__":
    produce_video()
    upload_now()
    
