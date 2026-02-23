name: Fail Fast Bot
on:
  workflow_dispatch:
  schedule:
    - cron: '0 14 * * *'

jobs:
  check-and-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # ১. এনভায়রনমেন্ট সেটআপ (১০ সেকেন্ড লাগবে)
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      # ২. আগেই সব টুলস ইন্সটল (না থাকলে এখানেই ফেল করবে)
      - name: Install Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
          pip install requests google-generativeai google-api-python-client duckduckgo-search mutagen numpy opencv-python-headless
          
      # ৩. মেইন কোড রান
      - name: Run Main Script
        run: python main.py
