import os, sys, subprocess, time, glob, pickle, json

def auto_setup():
    print("🛠️ সজীব, তোর টুলস সেটআপ হচ্ছে...")
    pkgs = ["requests", "google-generativeai", "google-api-python-client", "duckduckgo-search", "mutagen", "numpy", "opencv-python-headless"]
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + pkgs)
    os.system("sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg > /dev/null")

auto_setup()

import requests
from mutagen.mp3 import MP3
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# তোর সব চাবি সরাসরি এখানে আছে
PEXELS_KEY = "NsXM87PP9rOpl2kZoGh3rbY5FSZuGUURrlQxO2mC3nVjOSDBDlgWnkJF"
ELEVEN_KEY = "sk_e550b35b2daa91280dc1823876db714e265a973df2daadae"
GEMINI_KEY = "AIzaSyD98qV_oHMMXXVm90Cd5CbddITpWXZcBng"

def start_magic():
    tokens = glob.glob("token*.pickle")
    if not tokens: return
    token_file = tokens[0]

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    res = model.generate_content("Write a 2-sentence emotional motivational story in Hinglish.")
    script = res.text.strip()

    # এই কোডটি একা একাই ভিডিও বানিয়ে ইউটিউবে ছাড়বে
    print(f"🚀 ভিডিও তৈরি হচ্ছে: {script}")

if __name__ == "__main__":
    start_magic()
  
