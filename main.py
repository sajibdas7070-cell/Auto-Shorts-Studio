import os, sys, glob, json, time, asyncio, shutil, random
import requests
import edge_tts
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# ==========================================
# 🔧 অটো-ফিক্সার
# ==========================================
print("🔧 সিস্টেম রেডি হচ্ছে...")
found_tokens = glob.glob("*.pickle")
if found_tokens and not os.path.exists("token.pickle"):
    shutil.move(found_tokens[0], "token.pickle")

if not os.path.exists("token.pickle"):
    print("❌ টোকেন ফাইল নেই! আপলোড হবে না।")
    sys.exit(1)

# ==========================================
# 🔐 API KEYS
# ==========================================
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"

# ==========================================
# 🧠 মডিউল ১: ভাইরাল অ্যাটিটিউড ব্রেইন
# ==========================================
def get_viral_content(index):
    print(f"🧠 ভিডিও {index+1}: জেমিনি ভাইরাল টপিক খুঁজছে...")
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # এখানে অ্যাটিটিউড এবং ইমোশন মিক্স করা হয়েছে
        topics = ["Sigma Rule", "Fake Friends", "Success Revenge", "Dark Psychology", "Lone Wolf", "Mother's Love", "Broken Heart"]
        topic = random.choice(topics)
        
        prompt = f"""
        Act as a Viral Content Creator. Create a script for a YouTube Short about '{topic}'.
        Style: High Attitude, Deep Emotion, Killer Mindset.
        Language: Hinglish (mix of Hindi & English).
        Length: Must be around 140-150 words (to cover 55-60 seconds).
        
        Output ONLY JSON:
        {{
            "script": "The spoken text here...",
            "visual_keywords": ["keyword1", "keyword2", "keyword3"],
            "title": "A viral clickbait title with emojis",
            "tags": "#tag1 #tag2 #tag3"
        }}
        """
        res = model.generate_content(prompt)
        return json.loads(res.text.replace("```json", "").replace("```", "").strip())
    except:
        return {
            "script": "Jab waqt bura hota hai na, tab gair to kya, apne bhi rang dikhate hain. Lekin yaad rakhna, sher akela hi shikar karta hai.",
            "visual_keywords": ["lion walking", "sad man rain", "fire"],
            "title": "Time Changes Everything 🔥 #Attitude #Shorts",
            "tags": "#sigma #motivation #viral"
        }

# ==========================================
# 🎙️ মডিউল ২: ভয়েস (ইমোশনাল টিউন)
# ==========================================
async def generate_voice(text, filename):
    try:
        # ভয়েস পিচ এবং স্পিড একটু স্লো করা হয়েছে যাতে 'Heavy Attitude' লাগে
        communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="-5%", pitch="-2Hz")
        await communicate.save(filename)
    except:
        pass

# ==========================================
# 🎬 মডিউল ৩: ক্রিয়েটিভ এডিটিং (৩টি ক্লিপ)
# ==========================================
def download_clip(query, filename):
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait&size=medium"
    try:
        r = requests.get(url, headers=headers)
        v_link = r.json()['videos'][0]['video_files'][0]['link']
        with open(filename, "wb") as f: f.write(requests.get(v_link).content)
        return True
    except:
        return False

def produce_video(index):
    data = get_viral_content(index)
    script = data['script']
    print(f"📝 স্ক্রিপ্ট সাইজ: {len(script.split())} শব্দ")

    # ১. ভয়েস
    asyncio.run(generate_voice(script, "voice.mp3"))

    # ২. মাল্টি-ক্লিপ ডাউনলোড (৩টি আলাদা সিন)
    print("⬇️ সিন ডাউনলোড করছি...")
    clips = []
    for i, keyword in enumerate(data['visual_keywords'][:3]):
        clip_name = f"clip_{i}.mp4"
        if download_clip(keyword, clip_name):
            clips.append(clip_name)
    
    if not clips:
        # ব্যাকআপ ভিডিও
        download_clip("dark aesthetic", "clip_0.mp4")
        clips.append("clip_0.mp4")

    # ৩. মিউজিক
    with open("bg.mp3", "wb") as f: f.write(requests.get("https://cdn.pixabay.com/download/audio/2022/03/09/audio_c8c8a73467.mp3").content)

    # ৪. FFmpeg ম্যাজিক এডিটিং (Join Clips + Resize)
    print("🎬 ভিডিও এডিটিং চলছে...")
    
    # সব ক্লিপকে ১০৮০x১৯২০ সাইজে কনভার্ট করা হবে
    filter_complex = ""
    inputs = ""
    for i, clip in enumerate(clips):
        inputs += f"-i {clip} "
        filter_complex += f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v{i}];"
    
    concat_part = "".join([f"[v{i}]" for i in range(len(clips))])
    
    # সব জোড়া লাগিয়ে ফাইনাল ভিডিও
    cmd = (
        f'ffmpeg -y {inputs} -i voice.mp3 -i bg.mp3 '
        f'-filter_complex '
        f'"{filter_complex}{concat_part}concat=n={len(clips)}:v=1:a=0[v];'
        f'[2+n:a]volume=0.2[bg];[{1+n}:a][bg]amix=inputs=2:duration=first[a]" '
        f'-map "[v]" -map "[a]" -c:v libx264 -preset fast -shortest final.mp4'
    )
    # জটিল কমান্ড যদি ফেইল করে, সিম্পল ১টা ভিডিও দিয়ে ব্যাকআপ
    if os.system(cmd) != 0:
        print("⚠️ মাল্টি-ক্লিপ এডিটিং ফেইল, সিঙ্গেল ক্লিপ ব্যবহার করছি...")
        os.system(f'ffmpeg -y -stream_loop -1 -i clip_0.mp4 -i voice.mp3 -i bg.mp3 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v];[2:a]volume=0.2[bg];[1:a][bg]amix=inputs=2:duration=first[a]" -map "[v]" -map "[a]" -c:v libx264 -shortest final.mp4')

    return data # টাইটেল ও ট্যাগ রিটার্ন করবে

# ==========================================
# 🚀 লুপ আপলোড সিস্টেম (১০টি ভিডিও)
# ==========================================
def start_marathon():
    # ১০ বার লুপ চলবে
    for i in range(10): 
        print(f"\n🎥 ভিডিও প্রসেসিং {i+1}/10 শুরু...")
        try:
            video_data = produce_video(i)
            
            # আপলোড
            print("🚀 আপলোড হচ্ছে...")
            with open("token.pickle", "rb") as token: creds = pickle.load(token)
            youtube = build("youtube", "v3", credentials=creds)
            
            request = youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": video_data['title'],
                        "description": f"{video_data['script']}\n\n{video_data['tags']}",
                        "categoryId": "27"
                    },
                    "status": {"privacyStatus": "public"}
                },
                media_body=MediaFileUpload("final.mp4", chunksize=-1, resumable=True)
            )
            res = request.execute()
            print(f"✅ ভিডিও {i+1} সাকসেস! Link: https://youtu.be/{res['id']}")
            
            # ক্লিনআপ
            for f in glob.glob("*.mp4") + glob.glob("*.mp3"):
                try: os.remove(f)
                except: pass
            
            # ১০ মিনিট বিশ্রাম (যাতে স্প্যাম না ধরে)
            if i < 9:
                print("⏳ ১০ মিনিটের বিরতি... (Spam Protection)")
                time.sleep(600) 

        except Exception as e:
            print(f"❌ ভিডিও {i+1} এরর: {e}")
            time.sleep(60) # ১ মিনিট পর আবার চেষ্টা করবে

if __name__ == "__main__":
    start_marathon()
                
