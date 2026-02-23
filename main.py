name: Real Upload Bot
on:
  workflow_dispatch:
  schedule:
    - cron: '0 14 * * *'

jobs:
  fix-and-run:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v3

      - name: 1. Setup Environment
        uses: actions/setup-python@v4
        with:
          python-version: '3.10' 

      - name: 2. Fix Token Filename (ম্যাজিক ফিক্স)
        run: |
          # যেকোনো pickle ফাইল খুঁজে সেটাকে token.pickle নাম দেবে
          find . -maxdepth 1 -name "*.pickle" -exec mv "{}" token.pickle \;
          echo "ফাইল চেক করা হচ্ছে:"
          ls -la token.pickle

      - name: 3. Install Requirements
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
          pip install requests google-generativeai google-api-python-client duckduckgo-search mutagen numpy edge-tts

      - name: 4. Run Script
        run: python main.py
