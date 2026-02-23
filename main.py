import os, sys, glob, json, time, random, asyncio, shutil
import requests
import edge_tts
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# ==========================================
# 🔧 অটো-ফিক্সার (তোর ফাইল প্রবলেম সলভ)
# ==========================================
print("🔧 সিস্টেম রিপেয়ার শুরু...")
found_tokens = glob.glob("*.pickle")
if not found_tokens:
    print("❌ মহাবিপদ! কোনো .pickle ফাইল নেই! ফাইল আপলোড কর।")
    sys.exit(1)
else:
    # যেই নামেই থাকুক, সেটাকে token.pickle বানিয়ে নেবে
    print(f"✅ ফাইল পাওয়া গেছে: {found_tokens[0]}")
    shutil.move(found_tokens[0], "token.pickle")
    print("✅ ফাইলের নাম ঠিক করা হয়েছে: token.pickle")

# ==========================================
# 🔐 তোর চাবি (API KEYS)
# ==========================================
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"

# ==========================================
# 🧠 রিসার্চ মডিউল: জেমিনি ভিজুয়াল ডিরেক্টর
# ==========================================
def get_viral_plan():
    print("🧠 জেমিনি এখন ভিডিও প্ল্যান করছে...")
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # রিসার্চ প্রম্পট: ইমোশন + ভিজুয়াল সিন
        prompt = """
        You are a generic motivational video creator.
        Output ONLY JSON:
        {
            "script": "One deep philosophical sentence in Hinglish about life struggle.",
            "visual": "A specific English search term for Pexels video (e.g. 'sad man rain', 'stormy ocean')",
            "music": "sad"
        }
        """
        res = model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"script": "Jab sab darwaye band ho jaye, tab naya raasta khulta hai.", "visual": "dark tunnel light", "music": "sad"}

# ==========================================
# 🎙️ ভয়েস মডিউল: Edge-TTS (সবচেয়ে সেফ)
# ==========================================
async def generate_voice(text):
    print(f"🎙️ ভয়েস দিচ্ছি: {text}")
    try:
        # হিন্দি সিনেমাটিক ভয়েস (Madhur)
        communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
        await communicate.save("voice.mp3")
    except Exception as e:
        print(f"❌ ভয়েস এরর: {e}")
        sys.exit(1)

# ==========================================
# 🎬 প্রোডাকশন মডিউল (ভিডিও + অডিও)
# ==========================================
def produce_video():
    plan = get_viral_plan()
    script = plan['script']
    print(f"📝 স্ক্রিপ্ট: {script}")

    # ১. ভয়েস তৈরি
    asyncio.run(generate_voice(script))

    # ২. ভিডিও ডাউনলোড (Pexels)
    print(f"⬇️ ভিডিও খুঁজছি: {plan['visual']}")
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={plan['visual']}&per_page=1&orientation=portrait"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if data['videos']:
            v_link = data['videos'][0]['video_files'][0]['link']
            with open("raw.mp4", "wb") as f: f.write(requests.get(v_link).content)
        else:
            raise Exception("No video")
    except:
        print("⚠️ ভিডিও পাওয়া যায়নি, ব্যাকআপ দিচ্ছি...")
        with open("raw.mp4", "wb") as f: f.write(requests.get("https://player.vimeo.com/external/371835695.sd.mp4?s=12345").content)

    # ৩. মিউজিক ডাউনলোড
    print("🎵 মিউজিক দিচ্ছি...")
    with open("bg.mp3", "wb") as f: f.write(requests.get("https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3").content)

    # ৪. রিসার্চ এডিটিং (FFmpeg Magic)
    # - Saturation 1.2 (কালার বুস্ট)
    # - Scale & Crop (ফুল স্ক্রিন ফিক্স)
    print("🎬 ফাইনাল রেন্ডারিং চলছে...")
    try:
        audio_dur = MP3("voice.mp3").info.length
    except: audio_dur = 10

    cmd = (
        f'ffmpeg -y -stream_loop -1 -i raw.mp4 -i voice.mp3 -i bg.mp3 '
        f'-filter_complex '
        f'"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,eq=saturation=1.2[v];'
        f'[2:a]volume=0.2[bg];[1:a][bg]amix=inputs=2:duration=first[a]" '
        f'-map "[v]" -map "[a]" -c:v libx264 -preset fast -t {audio_dur} final.mp4'
    )
    os.system(cmd)

# ==========================================
# 🚀 আপলোড মডিউল
# ==========================================
def upload_now():
    print("🚀 আপলোড শুরু...")
    if not os.path.exists("final.mp4"):
        print("❌ ভিডিও তৈরি হয়নি! FFmpeg ফেল করেছে।")
        sys.exit(1)

    try:
        # ফাইল নাম ফিক্স করার পর 'token.pickle' নামেই লোড হবে
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
        
        youtube = build("youtube", "v3", credentials=creds)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "Deep Reality 🌑 #Shorts #Motivation",
                    "description": "Motivational video generated by AI.",
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
        )
        res = request.execute()
        print(f"🎉 সাকসেস! ভিডিও আপলোড হয়েছে: https://youtu.be/{res['id']}")
    except Exception as e:
        print(f"❌ আপলোড এরর: {e}")
        sys.exit(1)

if __name__ == "__main__":
    produce_video()
    upload_now()
    
