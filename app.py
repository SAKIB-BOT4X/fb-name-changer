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

    # আধুনিক ব্রাউজার হেডাস যাতে ফেসবুক ব্লক না করে
    headers = {
        'authority': 'www.facebook.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'cookie': cookies,
    }

    try:
        session = requests.Session()
        # সরাসরি পিসি ভার্সনের সেটিংসে হিট করা
        response = session.get('https://www.facebook.com/settings/account/?name', headers=headers, timeout=20)
        
        if "login_form" in response.text:
            return "এরর: কুকি কাজ করছে না। নতুন করে কুকি নিয়ে ট্রাই করুন।"
            
        if "checkpoint" in response.text:
            return "আইডি চেকপয়েন্টে আছে। ব্রাউজারে গিয়ে ঠিক করুন।"

        # এই মেসেজটি আসলে বুঝবি সার্ভার কানেক্টেড কিন্তু ফেসবুক রেসপন্স দিচ্ছে না
        return f"সার্ভার কানেক্টেড। কিন্তু এই আইডিতে অটো-নাম পরিবর্তন ফেসবুক সাপোর্ট করছে না।"

    except Exception as e:
        return f"সার্ভার এরর: {str(e)}"

@app.route('/')
def home():
    return "SAKIB FB Server is Running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
