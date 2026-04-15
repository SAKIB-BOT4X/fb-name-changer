import requests
import re
from flask import Flask, request
import os

app = Flask(__name__)

def get_headers(cookie):
    return {
        'authority': 'mbasic.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    }

@app.route('/fb-change', methods=['POST'])
def change_name():
    new_name = request.form.get('fb_name')
    cookies = request.form.get('fb_cookie')

    if not new_name or not cookies:
        return "ভুল! নাম বা কুকি পাওয়া যায়নি।"

    session = requests.Session()
    headers = get_headers(cookies)
    
    try:
        # মবাইল ভার্সন ব্যবহার করা নিরাপদ
        res = session.get('https://mbasic.facebook.com/settings/account/?name', headers=headers, timeout=20)
        
        if "checkpoint" in res.text or "login_form" in res.text:
            return "এরর: আইডি চেকপয়েন্টে আছে অথবা কুকি কাজ করছে না।"

        # Regex-এ সেফলি ডাটা খোঁজা (যাতে 'NoneType' এরর না আসে)
        fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', res.text)
        jazoest_match = re.search(r'name="jazoest" value="(.*?)"', res.text)
        action_match = re.search(r'action="(/settings/account/name/review/.*?)"', res.text)

        # যদি কোনো ডাটা খুঁজে না পায়
        if not fb_dtsg_match or not jazoest_match or not action_match:
            return "এরর: ফেসবুক পেজ থেকে ডাটা নিতে পারছে না। কুকি পরিবর্তন করুন।"

        # ডাটাগুলো ভেরিয়েবলে নেওয়া
        fb_dtsg = fb_dtsg_match.group(1)
        jazoest = jazoest_match.group(1)
        action_url = action_match.group(1)
        
        data = {
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'primary_first_name': new_name,
            'primary_last_name': '', 
            'save': 'Review Change'
        }

        response = session.post(f'https://mbasic.facebook.com{action_url}', headers=headers, data=data, timeout=25)

        if "Review your name change" in response.text or "password" in response.text.lower():
            return f"সফল! '{new_name}' রিভিউতে গেছে। ফেসবুকে গিয়ে চেক করুন।"
        else:
            return "ফেসবুক রিজেক্ট করেছে। কুকি বা নামের স্টাইল পরিবর্তন করে দেখুন।"

    except Exception as e:
        return f"সার্ভার এরর: {str(e)}"

@app.route('/')
def home():
    return "SAKIB FB Server is Running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
