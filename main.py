import os, sys, glob, json, time, asyncio, shutil, random, subprocess, pickle
import requests, edge_tts
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# 🛠️ রিসার্চ মডিউল ১: জিরো-এরর ফিক্সার
# ==========================================
def init_system():
    print("🔧 সিস্টেম ডায়াগনস্টিক...")
    # টোকেন ফাইল অটো-রিনেম (রিসার্চ ৩ অনুযায়ী)
    found = glob.glob("*.pickle")
    if found and not os.path.exists("token.pickle"):
        shutil.move(found[0], "token.pickle")
        print(f"✅ টোকেন ডিটেক্টেড: {found[0]}")
    if not os.path.exists("token.pickle"):
        print("❌ টোকেন ফাইল নেই!"); sys.exit(1)

# API KEYS
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"

# ==========================================
# 🧠 রিসার্চ মডিউল ২: ভাইরাল টপিক জেনারেটর
# ==========================================
def get_viral_content():
    print("🧠 জেমিনি ভাইরাল রিসার্চ করছে...")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # রিসার্চ ২ অনুযায়ী: ৬০ সেকেন্ডের ইমোশনাল অ্যাটিটিউড স্ক্রিপ্ট
    prompt = """
    Create a viral 60-second YouTube Short script. 
    Topic: Sigma Attitude / Dark Psychology / Success.
    Language: Hinglish (Hindi + English mix).
    Style: Emotional, Deep, Attitude.
    Output ONLY JSON:
    {"script": "Full script here...", "visual": "search keyword for pexels", "title": "Viral Title", "tags": "#attitude #sigma"}
    """
    try:
        res = model.generate_content(prompt)
        return json.loads(res.text.replace("```json", "").replace("```", "").strip())
    except:
        return {"script": "Jab tum akele chalna sikh jaate ho, tab tum asli power mehsoos karte ho.", "visual": "dark city lone man", "title": "Power of Silence 🌑", "tags": "#sigma #shorts"}

# ==========================================
# 🎙️ রিসার্চ মডিউল ৩: ডিপ ভয়েস ইঞ্জিন
# ==========================================
async def generate_voice(text):
    # রিসার্চ ৪ অনুযায়ী: গম্ভীর এবং ইমোশনাল ভয়েস
    voice_file = "voice.mp3"
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="-5%", pitch="-3Hz")
    await communicate.save(voice_file)
    return voice_file

# ==========================================
# 🎬 রিসার্চ মডিউল ৪: সিনেমাটিক রেন্ডারিং (FFmpeg)
# ==========================================
def produce_cinematic_video(data):
    print("🎬 সিনেমাটিক রেন্ডারিং শুরু...")
    
    # ১. অডিও দৈর্ঘ্য
    audio_dur = MP3("voice.mp3").info.length

    # ২. ভিডিও সোর্সিং (Pexels)
    headers = {"Authorization": PEXELS_KEY}
    v_search = requests.get(f"https://api.pexels.com/videos/search?query={data['visual']}&per_page=1&orientation=portrait", headers=headers).json()
    v_url = v_search['videos'][0]['video_files'][0]['link']
    with open("raw.mp4", "wb") as f: f.write(requests.get(v_url).content)

    # ৩. মিউজিক (Ducking Effect)
    music_url = "https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3"
    with open("bg.mp3", "wb") as f: f.write(requests.get(music_url).content)

    # ৪. রিসার্চ ৫: হাই-প্রোফাইল FFmpeg (Blur Padding + Sidechain Compression)
    # এই কমান্ডটি ভিডিওর পেছনের কালো অংশ ব্লার করে দেবে এবং কথা শুরু হলে মিউজিক কমিয়ে দেবে
    cmd = (
        f'ffmpeg -y -stream_loop -1 -i raw.mp4 -i voice.mp3 -i bg.mp3 '
        f'-filter_complex '
        f'"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[fg];'
        f'[0:v]scale=1080:1920,boxblur=20:10[bg_blur];[bg_blur][fg]overlay=(W-w)/2:(H-h)/2[v];'
        f'[2:a]volume=0.2[music];[music][1:a]sidechaincompress=threshold=0.1:ratio=20:attack=50:release=200[a]" '
        f'-map "[v]" -map "[a]" -c:v libx264 -t {audio_dur} final.mp4'
    )
    subprocess.run(cmd, shell=True)

# ==========================================
# 🚀 রিসার্চ মডিউল ৫: অটো-আপলোড
# ==========================================
def upload_to_youtube(data):
    print("🚀 ইউটিউবে আপলোড হচ্ছে...")
    with open("token.pickle", "rb") as t: creds = pickle.load(t)
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": data['title'], "description": data['script'] + "\n" + data['tags'], "categoryId": "27"},
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
    )
    res = request.execute()
    print(f"✅ ভিডিও লাইভ! ID: {res['id']}")

# ==========================================
# ⚡ এক্সিকিউশন
# ==========================================
if __name__ == "__main__":
    init_system()
    content = get_viral_content()
    asyncio.run(generate_voice(content['script']))
    produce_cinematic_video(content)
    upload_to_youtube(content)
    print("🌟 আজকের কাজ সফলভাবে সম্পন্ন!")
    
