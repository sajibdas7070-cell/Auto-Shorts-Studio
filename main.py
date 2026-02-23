import os, random, subprocess, json, asyncio, base64, pickle, time
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ১. সেটিংস (গিটহাব সিক্রেটস থেকে অটোমেটিক নেবে)
GEMINI_KEY = os.getenv("GEMINI_KEY")
PICKLE_CONTENT = os.getenv("PICKLE_CONTENT") # token.pickle এর কোড

# ২. ভাইরাল মুভি রিসার্চার (রাশিয়া/পোল্যান্ড ফোকাস)
def search_viral_content():
    queries = [
        "top russian action movie trailers 2026",
        "popular polish web series clips trending",
        "viral european sci-fi movie scenes"
    ]
    q = random.choice(queries)
    # ১০টি রেজাল্ট থেকে একটি র্যান্ডম ভিডিও বেছে নেবে
    cmd = f'yt-dlp "ytsearch10:{q}" --get-id --get-title --match-filter "duration > 600"'
    res = subprocess.check_output(cmd, shell=True).decode().split('\n')
    idx = random.randrange(0, len(res)-1, 2)
    return {"title": res[idx], "url": f"https://youtube.com/watch?v={res[idx+1]}"}

# ৩. কপিরাইট ইভেশন এডিটর (Advanced FFmpeg)
def smart_edit(input_f, output_f):
    # ভিডিও ফ্লিপ, জুম এবং অডিও পিচ পরিবর্তন করবে যাতে স্ট্রাইক না আসে
    cmd = [
        'ffmpeg', '-y', '-i', input_f,
        '-vf', "hflip,scale=1280:720,eq=brightness=0.05:contrast=1.3,zoompan=z='min(zoom+0.001,1.1)':d=1:s=1280x720",
        '-af', "asetrate=44100*0.97,atempo=1.03",
        '-t', '900', output_f # প্রথম ১৫ মিনিট প্রসেস করবে
    ]
    subprocess.run(cmd)

# ৪. এআই হিন্দি ডাবিং স্ক্রিপ্ট ও টাইটেল
def get_hindi_metadata(title):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Movie: {title}. Create a viral Hindi Clickbait Title and Tags for YouTube. Format: JSON"
    res = model.generate_content(prompt)
    return json.loads(res.text.replace("```json", "").replace("```", ""))

# ৫. ইউটিউব আপলোডার
def upload_to_yt(file, meta):
    creds = pickle.loads(base64.b64decode(PICKLE_CONTENT))
    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {"title": meta['title'], "description": "Viral Movie Summary in Hindi #trending", "categoryId": "24"},
        "status": {"privacyStatus": "public"}
    }
    youtube.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(file, resumable=True)).execute()

async def start():
    data = search_viral_content()
    print(f"🎯 Working on: {data['title']}")
    subprocess.run(['yt-dlp', '-f', 'bestvideo[height<=720]+bestaudio/best', '-o', 'raw.mp4', data['url']])
    meta = get_hindi_metadata(data['title'])
    smart_edit("raw.mp4", "final.mp4")
    upload_to_yt("final.mp4", meta)

if __name__ == "__main__":
    asyncio.run(start())
    
