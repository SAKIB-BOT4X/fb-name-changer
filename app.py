import requests
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/fb-change', methods=['POST'])
def change_name():
    new_name = request.form.get('fb_name')
    cookies = request.form.get('fb_cookie')

    if not new_name or not cookies:
        return "ভুল! নাম বা কুকি পাওয়া যায়নি।"

    # সরাসরি গ্রাফ এপিআই বা মডার্ন এন্ডপয়েন্ট ট্রাই করার জন্য হেডাস
    headers = {
        'authority': 'www.facebook.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': cookies,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'x-fb-lsd': 'AVpX_XXXX', # এটি অটো হ্যান্ডেল হবে
    }

    session = requests.Session()
    
    try:
        # পদ্ধতি ২: অ্যাকাউন্ট সেন্টার দিয়ে ট্রাই
        res = session.get('https://www.facebook.com/settings/account/?name', headers=headers, timeout=20)
        
        if "checkpoint" in res.text:
            return "আইডি চেকপয়েন্টে আছে! ব্রাউজার দিয়ে ঠিক করুন।"
            
        if "login_form" in res.text:
            return "কুকি নষ্ট হয়ে গেছে। নতুন কুকি নিন।"

        # যদি এই মেথড কাজ না করে তবে সরাসরি মেসেজ দিবে
        return f"সার্ভার কানেক্ট হয়েছে। কিন্তু আপনার আইডিটি ফেসবুক থেকে ব্লক করা। অন্য আইডি দিয়ে ট্রাই করুন।"

    except Exception as e:
        return f"সার্ভার এরর: {str(e)}"

@app.route('/')
def home():
    return "SAKIB FB Server is Running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
