import requests
import time
import threading

class Message:
    def __init__(self, bot, data):
        self.bot = bot
        self.text = data.get("text", "")
        self.from_id = data.get("sender_guid")
        self.chat_id = data.get("chat_guid")
        self.data = data

    def reply(self, text):
        self.bot.send_message(self.chat_id, text)


class Bot:
    def __init__(self, token):
        self.token = token
        self.handlers = []

    def send_message(self, chat_id, text):
        url = "https://messengerg2c20.iranlms.ir/v2/message/sendText"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"text": text, "chatGuid": chat_id}
        try:
            requests.post(url, headers=headers, json=payload)
        except Exception as e:
            print("Send message error:", e)

    def on_message(self, func):
        self.handlers.append(func)
        return func

    def _polling_loop(self, interval=1):
        last_id = None
        while True:
            try:
                url = "https://messengerg2c20.iranlms.ir/v2/message/getUpdates"
                headers = {"Authorization": f"Bearer {self.token}"}
                params = {"lastMessageId": last_id} if last_id else {}
                resp = requests.get(url, headers=headers, params=params).json()

                for msg in resp.get("messages", []):
                    last_id = msg["message_id"]
                    message = Message(self, msg)
                    for handler in self.handlers:
                        if callable(handler):
                            handler(message)
            except Exception as e:
                print("Polling error:", e)
            time.sleep(interval)

    def start_polling(self, interval=1):
        t = threading.Thread(target=self._polling_loop, args=(interval,), daemon=True)
        t.start()
        print("🤖 Bot started polling...")

    def start_command(self, chat_id, text="سلام! ربات آماده است."):
        self.send_message(chat_id, text)
