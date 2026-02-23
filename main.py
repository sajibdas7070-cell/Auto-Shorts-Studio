import os, sys, glob, json, time, asyncio, shutil, subprocess, pickle
import requests, edge_tts
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# 🛠️ রিসার্চ মডিউল ১: সিস্টেম ফিক্সার
# ==========================================
def init_system():
    print("⚙️ সিস্টেম ডায়াগনস্টিক চলছে...")
    found = glob.glob("*.pickle")
    if found and not os.path.exists("token.pickle"):
        shutil.move(found[0], "token.pickle")
        print(f"✅ টোকেন ডিটেক্টেড এবং রিনেমড: {found[0]} -> token.pickle")
    if not os.path.exists("token.pickle"):
        print("❌ এরর: টোকেন ফাইল পাওয়া যায়নি!"); sys.exit(1)

# API KEYS
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"

# ==========================================
# 🧠 রিসার্চ মডিউল ২: ভাইরাল ট্রেন্ড ইঞ্জিন
# ==========================================
def get_viral_content():
    print("🧠 জেমিনি ভাইরাল রিসার্চ করছে...")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = """
    Generate a viral 60-second YouTube Short script. 
    Niche: Sigma Attitude / Dark Motivation / Deep Truth.
    Format: Output ONLY valid JSON:
    {"script": "Spoken text in Hinglish (deep/emotional)", "visual": "search keyword for pexels", "title": "Viral Title", "tags": "#sigma #shorts"}
    """
    try:
        res = model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"script": "Waqt sabka badalta hai, bas thodi si mehnat aur sabr chahiye.", "visual": "dark motivation", "title": "Deep Reality 🌑", "tags": "#motivation #shorts"}

# ==========================================
# 🎬 রিসার্চ মডিউল ৩: সিনেমাটিক এডিটিং (Fixed FFmpeg)
# ==========================================
async def produce_cinematic_video(data):
    print("🎙️ ভয়েস তৈরি হচ্ছে...")
    await edge_tts.Communicate(data['script'], "hi-IN-MadhurNeural", pitch="-3Hz", rate="-5%").save("voice.mp3")
    
    print("⬇️ ভিডিও এবং মিউজিক নামানো হচ্ছে...")
    headers = {"Authorization": PEXELS_KEY}
    v_res = requests.get(f"https://api.pexels.com/videos/search?query={data['visual']}&per_page=1&orientation=portrait", headers=headers).json()
    v_url = v_res['videos'][0]['video_files'][0]['link']
    with open("raw.mp4", "wb") as f: f.write(requests.get(v_url).content)
    
    # ব্যাকগ্রাউন্ড মিউজিক (অ্যান্টি-ব্লক ডাউনলোড)
    m_url = "https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3"
    r = requests.get(m_url, headers={'User-Agent': 'Mozilla/5.0'})
    with open("bg.mp3", "wb") as f: f.write(r.content)

    print("🎬 এডিটিং চলছে (Blur Padding + Audio Ducking)...")
    audio_dur = MP3("voice.mp3").info.length

    # নতুন ফিক্সড ফিল্টার চেইন
    cmd = [
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', 'raw.mp4',
        '-i', 'voice.mp3',
        '-i', 'bg.mp3',
        '-filter_complex',
        '[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[fg];'
        '[0:v]scale=1080:1920,boxblur=20:10[bg_blur];'
        '[bg_blur][fg]overlay=(W-w)/2:(H-h)/2[v];'
        '[2:a]volume=0.2[music];[music][1:a]sidechaincompress=threshold=0.1:ratio=20:attack=50:release=200[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-t', str(audio_dur), 'final.mp4'
    ]
    subprocess.run(cmd)

# ==========================================
# 🚀 আপলোড মডিউল
# ==========================================
def upload_now(data):
    if not os.path.exists("final.mp4"):
        print("❌ এরর: ভিডিও ফাইল (final.mp4) তৈরি হয়নি! FFmpeg এ সমস্যা হয়েছে।"); sys.exit(1)
        
    print("🚀 ইউটিউবে আপলোড হচ্ছে...")
    with open("token.pickle", "rb") as t: creds = pickle.load(t)
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": data['title'], "description": f"{data['script']}\n\n{data['tags']}", "categoryId": "27"},
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("final.mp4", resumable=True)
    )
    request.execute()
    print("🎉 সাকসেস! ভিডিও আপলোড সম্পন্ন।")

if __name__ == "__main__":
    init_system()
    content = get_viral_content()
    asyncio.run(produce_cinematic_video(content))
    upload_now(content)
    
