import os, sys, glob, json, random, time, requests, asyncio
import edge_tts  # ফ্রি ব্যাকআপ ভয়েস
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==============================================
# 🔐 তোর চাবিগুলো (API KEYS)
# ==============================================
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"
ELEVEN_KEY = "sk_e550b35b2daa91280dc1823876db714e265a973df2daadae"

# ==============================================
# 🧠 মডিউল ১: জেমিনি (এরর প্রুফ)
# ==============================================
def get_script():
    print("🧠 জেমিনি স্ক্রিপ্ট লিখছে...")
    try:
        genai.configure(api_key=GEMINI_KEY)
        # মডেল পরিবর্তন করে 'gemini-pro' দেওয়া হলো যা সবচেয়ে স্টেবল
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = """
        Write a viral 2-sentence emotional motivation in Hinglish (Hindi+English).
        Output JSON: {"script": "text", "visual": "English keyword for Pexels video"}
        """
        res = model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"⚠️ জেমিনি এরর ({e}), ব্যাকআপ স্ক্রিপ্ট দিচ্ছি...")
        return {
            "script": "Jab waqt bura ho, tab chup rehna hi sabse badi taqat hoti hai.",
            "visual": "sad man rain dark"
        }

# ==============================================
# 🎙️ মডিউল ২: ভয়েস (ডুয়াল ইঞ্জিন)
# ==============================================
async def generate_voice(text):
    print("🎙️ ভয়েস তৈরি করার চেষ্টা করছি...")
    
    # অপশন ১: ইলেভেন ল্যাবস (টাকা/ক্রেডিট থাকলে)
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
        headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
        data = {"text": text, "model_id": "eleven_multilingual_v2"}
        r = requests.post(url, json=data, headers=headers)
        
        if r.status_code == 200:
            with open("voice.mp3", "wb") as f: f.write(r.content)
            print("✅ ইলেভেন ল্যাবস সাকসেস!")
            return True
        else:
            print(f"⚠️ ইলেভেন ল্যাবস ফেইল (Quota/Key Error)।")
    except:
        pass

    # অপশন ২: Edge-TTS (আজীবন ফ্রি ব্যাকআপ)
    print("🔄 ব্যাকআপ ভয়েস (Edge-TTS) চালু করছি...")
    try:
        # হিন্দি সিনেমাটিক ভয়েস
        communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
        await communicate.save("voice.mp3")
        print("✅ ব্যাকআপ ভয়েস রেডি!")
        return True
    except Exception as e:
        print(f"❌ সব ভয়েস ইঞ্জিন ফেইল! {e}")
        return False

# ==============================================
# 🎬 মেইন স্টুডিও
# ==============================================
def run_studio():
    # ১. স্ক্রিপ্ট
    data = get_script()
    script = data['script']
    query = data['visual']
    print(f"📝 {script}")

    # ২. ভয়েস (Async কল)
    if not asyncio.run(generate_voice(script)):
        sys.exit(1)

    # ৩. ভিডিও ডাউনলোড (Pexels)
    print("⬇️ ভিডিও নামাচ্ছি...")
    p_headers = {"Authorization": PEXELS_KEY}
    p_url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
    
    try:
        r = requests.get(p_url, headers=p_headers)
        if r.status_code == 200 and r.json().get('videos'):
            v_link = r.json()['videos'][0]['video_files'][0]['link']
            with open("raw.mp4", "wb") as f: f.write(requests.get(v_link).content)
        else:
            raise Exception("No video found")
    except:
        print("⚠️ ভিডিও পাওয়া যায়নি, ডিফল্ট ভিডিও দিচ্ছি...")
        # এখানে একটা সেফটি ভিডিও লিঙ্ক দেওয়া হলো
        safe_url = "https://player.vimeo.com/external/371835695.sd.mp4?s=12345" 
        with open("raw.mp4", "wb") as f: f.write(requests.get(safe_url).content)

    # ৪. এডিটিং (FFmpeg)
    print("🎬 এডিটিং চলছে...")
    # মিউজিক ডাউনলোড
    m_url = "https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3"
    with open("bg.mp3", "wb") as f: f.write(requests.get(m_url).content)

    try:
        dur = MP3("voice.mp3").info.length
    except:
        dur = 10 # যদি অডিও ফাইল করাপ্ট হয়

    # সেইফ এডিটিং কমান্ড
    cmd = (
        f'ffmpeg -y -stream_loop -1 -i raw.mp4 -i voice.mp3 -i bg.mp3 '
        f'-filter_complex '
        f'"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v];'
        f'[2:a]volume=0.2[bg];[1:a][bg]amix=inputs=2:duration=first[a]" '
        f'-map "[v]" -map "[a]" -c:v libx264 -t {dur} final.mp4'
    )
    os.system(cmd)

    # ৫. ইউটিউব আপলোড
    print("☁️ আপলোড করছি...")
    tokens = glob.glob("token*.pickle")
    if not tokens:
        print("❌ টোকেন ফাইল নেই! ভিডিও 'final.mp4' নামে সেভ আছে, কিন্তু আপলোড হবে না।")
        sys.exit(0) # এরর না দেখিয়ে শান্তভাবে বের হবে
        
    try:
        creds = json.load(open(tokens[0])) if tokens[0].endswith(".json") else pickle.load(open(tokens[0], "rb"))
        youtube = build('youtube', 'v3', credentials=creds)
        
        youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "Deep Reality 🌑 #Shorts #Motivation",
                    "description": script,
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=MediaFileUpload("final.mp4", resumable=True)
        ).execute()
        print("🎉 ভিডিও সাকসেসফুলি আপলোড হয়েছে!")
    except Exception as e:
        print(f"⚠️ আপলোড এরর: {e}")

if __name__ == "__main__":
    run_studio()
