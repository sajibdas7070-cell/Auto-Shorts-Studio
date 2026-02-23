import os, sys, glob, json, random, time, requests
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==============================================
# 🔐 API KEYS (তোর চাবিগুলো)
# ==============================================
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"
ELEVEN_KEY = "sk_e550b35b2daa91280dc1823876db714e265a973df2daadae"

# ==============================================
# 🧠 রিসার্চ মডিউল ১: ভাইরাল ইন্টেলিজেন্স
# ==============================================
def get_viral_blueprint():
    print("🧠 জেমিনি ভিজুয়াল ডিরেক্টর মুডে কাজ করছে...")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # রিসার্চ-বেসড প্রম্পট: ইমোশন এবং ভিজুয়াল ডিটেইলস একসাথে চাইবে
    prompt = """
    Act as a professional YouTube Shorts Filmmaker. 
    Create a 'Dark Psychology' or 'Stoic Motivation' video plan.
    
    Output ONLY a JSON object with these keys:
    {
      "script": "The spoken text in Hinglish (Deep, heavy voice style, Max 2 sentences)",
      "visual_search": "English keyword for Pexels video (e.g., 'stormy ocean', 'man walking alone night', 'fire slow motion')",
      "title": "A clickbait title for YouTube Shorts",
      "tags": "5 viral hashtags"
    }
    """
    try:
        res = model.generate_content(prompt)
        clean_json = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"⚠️ ব্যাকআপ প্ল্যান অ্যাক্টিভ করা হলো: {e}")
        return {
            "script": "Jab duniya tumhare khilaf ho, tab samajh lena tum sahi raaste par ho.",
            "visual_search": "lion walking dark",
            "title": "Power of Silence 🔥 #Shorts",
            "tags": "#motivation #sigma #dark"
        }

# ==============================================
# 🎬 রিসার্চ মডিউল ২: সিনেমাটিক প্রোডাকশন
# ==============================================
def produce_masterpiece():
    # ১. প্ল্যান তৈরি
    blueprint = get_viral_blueprint()
    print(f"📝 স্ক্রিপ্ট: {blueprint['script']}")
    print(f"👀 দৃশ্য: {blueprint['visual_search']}")

    # ২. ভয়েস জেনারেশন (Adam Deep Voice)
    print("🎙️ ভয়েস রেকর্ড হচ্ছে...")
    v_url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    # স্টেবিলিটি বাড়িয়ে দেওয়া হয়েছে যাতে ভয়েস কাঁপা কাঁপা না শোনায়
    data = {"text": blueprint['script'], "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.6, "similarity_boost": 0.85}}
    
    r = requests.post(v_url, json=data, headers=headers)
    if r.status_code == 200:
        with open("voice.mp3", "wb") as f: f.write(r.content)
    else:
        print("❌ ভয়েস এরর! সিস্টেম বন্ধ হচ্ছে।"); sys.exit(1)

    # ৩. 4K/HD ভিডিও সোর্সিং (Pexels)
    print("⬇️ সিনেমাটিক ফুটেজ খোঁজা হচ্ছে...")
    p_headers = {"Authorization": PEXELS_KEY}
    p_url = f"https://api.pexels.com/videos/search?query={blueprint['visual_search']}&per_page=1&orientation=portrait&size=medium"
    
    try:
        v_res = requests.get(p_url, headers=p_headers).json()
        video_link = v_res['videos'][0]['video_files'][0]['link']
        with open("raw.mp4", "wb") as f: f.write(requests.get(video_link).content)
    except:
        print("❌ ভিডিও পাওয়া যায়নি!"); sys.exit(1)

    # ৪. ব্যাকগ্রাউন্ড স্কোর (Epic Music)
    bg_url = "https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3"
    with open("music.mp3", "wb") as f: f.write(requests.get(bg_url).content)

    # ৫. পোস্ট-প্রোডাকশন এডিটিং (FFmpeg Advanced)
    print("🎬 মাস্টারিং এবং কালার গ্রেডিং চলছে...")
    audio_dur = MP3("voice.mp3").info.length
    
    # রিসার্চ টেকনিক: 
    # - scale & crop: ভিডিওকে জোর করে 1080x1920 বানানো হবে।
    # - eq=saturation: কালার একটু বুস্ট করা হবে (সিনেমাটিক লুক)।
    # - volume mapping: মিউজিক ১৫% এবং ভয়েস ১০০% ভলিউমে মিক্স হবে।
    
    cmd = (
        f'ffmpeg -y -stream_loop -1 -i raw.mp4 -i voice.mp3 -i music.mp3 '
        f'-filter_complex '
        f'"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,eq=saturation=1.2[v];'
        f'[2:a]volume=0.15[bg];[1:a][bg]amix=inputs=2:duration=first[a]" '
        f'-map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 23 -t {audio_dur} final.mp4'
    )
    os.system(cmd)

    # ৬. ইউটিউব ডিস্ট্রিবিউশন
    print("🚀 আপলোড প্রসেস শুরু...")
    token_files = glob.glob("token*.pickle")
    if not token_files: print("❌ টোকেন নেই!"); sys.exit(1)
    
    try:
        creds = pickle.load(open(token_files[0], 'rb'))
        youtube = build('youtube', 'v3', credentials=creds)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": blueprint['title'],
                    "description": f"{blueprint['script']}\n\n{blueprint['tags']}",
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
        )
        request.execute()
        print("🎉 মিশন কমপ্লিট! ভিডিও আপলোড হয়েছে।")
    except Exception as e:
        print(f"❌ আপলোড ফেইল্ড: {e}")

if __name__ == "__main__":
    produce_masterpiece()
  
