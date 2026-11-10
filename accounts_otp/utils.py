# import requests
#
# # data = {'from': '50002710095173', 'to': 'phone_number', 'text': 'test sms'}
# # response = requests.post('https://console.melipayamak.com/api/send/simple/ad790de2df3a47f5982a68e55d03a901', json=data)
# # print(response.json())
from django.conf import settings

def send_sms(phone_number, code):
    """
    ارسال کد تایید به شماره تلفن کاربر
    """
    # متن پیامک
    text = f"""🛍 نازاستور

کد تایید شما: {code}

این کد تا 5 دقیقه اعتبار دارد."""

    # اطلاعات ارسال
    data = {
        'from': '50002710095173',
        'to': [phone_number],
        'text': text,
        'udh': ''
    }

    # ========== اصلاح: فقط کلید رو بذار، نه کل آدرس ==========

    # ======================================================

    print(f"📡 آدرس: {url}")
    print(f"📱 شماره: {phone_number}")
    print(f"🔑 کد: {code}")

    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"📡 وضعیت: {response.status_code}")
        print(f"📡 پاسخ: {response.text}")

        if response.status_code == 200:
            result = response.json()
            # بررسی موفقیت
            if result.get('value') or result.get('status') == 1:
                print(f"✅ پیامک ارسال شد")
                return True
            else:
                print(f"❌ خطا: {result}")
                return False
        else:
            print(f"❌ خطای HTTP: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ خطا: {e}")
        return False
