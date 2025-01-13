from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = '7868173689:AAHdzcmNP8yiKzmmcrxsWHmpgu47RxIjpV0'
CHAT_ID = '7240662021'

# تابع تولید کانفیگ WireGuard
def generate_config():
    import random
    import string

    # تولید کلیدها
    private_key = ''.join(random.choices(string.ascii_letters + string.digits + '+/=', k=44))
    public_key = ''.join(random.choices(string.ascii_letters + string.digits + '+/=', k=42)) + '=='

    # تولید آدرس IP تصادفی
    ip_ranges = ["52.0.0.0/11", "54.240.0.0/12", "18.0.0.0/8", "3.0.0.0/8"]
    range_selected = random.choice(ip_ranges)

    # محاسبه آدرس IP
    def generate_random_ip(cidr):
        import ipaddress
        network = ipaddress.IPv4Network(cidr, strict=False)
        return str(random.choice(list(network.hosts())))

    client_ip = generate_random_ip(range_selected)
    port = 51820
    dns = "1.1.1.1"

    # ساخت کانفیگ
    config = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}/32
DNS = {dns}

[Peer]
PublicKey = {public_key}
AllowedIPs = 0.0.0.0/0
Endpoint = {client_ip}:{port}
PersistentKeepalive = 25"""

    return config

# مسیر webhook برای دریافت دستورات ربات
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def telegram_webhook():
    data = request.json

    # چک کردن دستور `/gen`
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if text == "/gen":
            config = generate_config()

            # ارسال کانفیگ به کاربر
            send_message(chat_id, f"🌟 *WireGuard Config Generated:*\n\n```{config}```", parse_mode="Markdown")
            return "ok"

    return "no action"

# تابع ارسال پیام به تلگرام
def send_message(chat_id, text, parse_mode=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    requests.post(url, json=payload)

# اجرای سرور Flask
if __name__ == "__main__":
    app.run(port=5000)
