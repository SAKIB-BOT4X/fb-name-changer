import requests
import re
from flask import Flask, request
import os
import random

app = Flask(__name__)

# মাল্টিপল ইউজার এজেন্ট যাতে ফেসবুক সার্ভারকে সন্দেহ না করে
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
]

@app.route('/fb-change', methods=['POST'])
def change_name():
    new_name = request.form.get('fb_name')
    cookies = request.form.get('fb_cookie')
    
    if not new_name or not cookies:
        return "ভুল! নাম বা কুকি দেওয়া হয়নি।"

    session = requests.Session()
    headers = {
        'authority': 'mbasic.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': cookies,
        'user-agent': random.choice(USER_AGENTS),
        'sec-fetch-site': 'same-origin',
    }

    try:
        # ধাপ ১: সেটিংস পেজ থেকে টোকেন সংগ্রহ
        res = session.get('https://mbasic.facebook.com/settings/account/?name', headers=headers, timeout=20)
        
        if "checkpoint" in res.text:
            return "আইডি লক বা চেকপয়েন্টে আছে। ব্রাউজারে লগইন করুন।"
        
        fb_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', res.text)
        jazoest = re.search(r'name="jazoest" value="(.*?)"', res.text)
        action = re.search(r'action="(/settings/account/name/review/.*?)"', res.text)

        if not fb_dtsg or not action:
            return "ফেসবুক ডাটা হাইড করেছে। এই আইডিতে অটো-চেঞ্জ সম্ভব না।"

        # ধাপ ২: নাম পরিবর্তনের রিকোয়েস্ট পাঠানো
        data = {
            'fb_dtsg': fb_dtsg.group(1),
            'jazoest': jazoest.group(1),
            'primary_first_name': new_name,
            'primary_last_name': '', 
            'save': 'Review Change'
        }

        response = session.post(f'https://mbasic.facebook.com{action.group(1)}', headers=headers, data=data, timeout=20)

        if "Review your name change" in response.text or "সফল" in response.text:
            return f"সফল! '{new_name}' নামটি রিভিউতে পাঠানো হয়েছে।"
        else:
            return "ফেসবুক নাম গ্রহণ করেনি। সম্ভবত নামটির স্টাইল ফেসবুক সাপোর্ট করছে না।"

    except Exception as e:
        return f"সার্ভার এরর: {str(e)}"

@app.route('/')
def home():
    return "SAKIB ULTRA SERVER IS LIVE!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
