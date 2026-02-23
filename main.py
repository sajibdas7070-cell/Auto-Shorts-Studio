import os, sys, time, json, requests, asyncio
import edge_tts
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# ==============================================
# 🔐 তোর চাবিগুলো (API KEYS)
# ==============================================
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"
# ElevenLabs এর চাবি (না থাকলে সমস্যা নেই, ফ্রি ভয়েস আছে)
ELEVEN_KEY = "sk_e550b35b2daa91280dc1823876db714e265a973df2daadae" 

# ==============================================
# ১. টোকেন চেকার (ভিডিও বানানোর আগেই চেক হবে)
# ==============================================
print("🔍 টোকেন ফাইল চেক করছি...")
if not os.path.exists("token.pickle"):
    print("❌ মহাবিপদ! 'token.pickle' ফাইল পাওয়া যায়নি।")
    print("টিপস: run.yml ফাইলটি ঠিকমতো আপডেট করেছিস তো?")
    sys.exit(1) # লাল এরর দিয়ে বন্ধ হবে
print("✅ টোকেন ফাইল রেডি! ভিডিও বানানো শুরু...")

# ==============================================
# ২. কন্টেন্ট জেনারেশন
# ==============================================
def get_script():
    print("🧠 কাহিনী লেখা হচ্ছে...")
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-pro') # Pro মডেল সবচেয়ে ভালো
        response = model.generate_content("Write a 1-sentence deep motivation in Hinglish about success.")
        return response.text.strip()
    except:
        return "Jo khud par vishwas rakhte hain, wahi itihaas rachte hain."

async def make_voice(text):
    print(f"🎙️ ভয়েস দিচ্ছি: {text}")
    try:
        # ফ্রি এবং ফাস্ট ভয়েস (Edge-TTS)
        communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
        await communicate.save("voice.mp3")
    except Exception as e:
        print(f"❌ ভয়েস এরর: {e}")
        sys.exit(1)

# ==============================================
# ৩. ভিডিও মেকিং ইঞ্জিন
# ==============================================
def make_video():
    script = get_script()
    asyncio.run(make_voice(script))
    
    print("⬇️ ভিডিও নামাচ্ছি...")
    # Pexels থেকে ভিডিও
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=dark cinematic&per_page=1&orientation=portrait"
    try:
        r = requests.get(url, headers=headers)
        v_url = r.json()['videos'][0]['video_files'][0]['link']
        with open("raw.mp4", "wb") as f: f.write(requests.get(v_url).content)
    except:
        # ভিডিও না পেলে ব্যাকআপ ভিডিও
        print("⚠️ Pexels ভিডিও পায়নি, ব্যাকআপ দিচ্ছি...")
        with open("raw.mp4", "wb") as f: f.write(requests.get("https://player.vimeo.com/external/371835695.sd.mp4?s=12345").content)

    print("🎬 এডিটিং চলছে...")
    # মিউজিক
    with open("bg.mp3", "wb") as f: f.write(requests.get("https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3").content)
    
    # FFmpeg দিয়ে ভিডিও বানানো
    try:
        audio_len = MP3("voice.mp3").info.length
    except: audio_len = 10

    os.system(f'ffmpeg -y -stream_loop -1 -i raw.mp4 -i voice.mp3 -i bg.mp3 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v];[2:a]volume=0.2[bg];[1:a][bg]amix=inputs=2:duration=first[a]" -map "[v]" -map "[a]" -c:v libx264 -t {audio_len} final.mp4')

    if not os.path.exists("final.mp4"):
        print("❌ ভিডিও তৈরি হয়নি!")
        sys.exit(1)

# ==============================================
# ৪. ইউটিউব আপলোড (ফাইনাল টেস্ট)
# ==============================================
def upload_video():
    print("🚀 ইউটিউবে আপলোড শুরু...")
    try:
        # টোকেন লোড করা
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
        
        youtube = build("youtube", "v3", credentials=creds)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "Success Mindset 🔥 #Shorts #Motivation",
                    "description": "Powerful motivational quotes. #shorts #quotes",
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"} # সরাসরি পাবলিক হবে
            },
            media_body=MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
        )
        response = request.execute()
        print(f"🎉 ভিডিও আপলোড সফল! Video ID: {response['id']}")
        print("👉 এখনই ইউটিউব স্টুডিও চেক কর!")

    except Exception as e:
        print(f"❌ আপলোড ফেইল করেছে! কারণ: {e}")
        # এই লাইনটা নিশ্চিত করবে যে গিটহাবে লাল ক্রস দেখাবে
        sys.exit(1)

if __name__ == "__main__":
    make_video()
    upload_video()
      
