from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from db import DBHelper
import json
import requests
import time
import urllib
import telegram_send
import threading

TOKEN = "1501745118:AAHX9J4n9UoANIY03R4mP2TH11EJPieky2c"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

app = Flask(__name__)
CORS(app)
exit_event = threading.Event()
states = ["Kerala"]
cities = { "Kerala": ["Ernakulam", "Alappuzha"] }

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def echo_all(updates, dataBase):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        username = update["message"]["chat"]["first_name"]
        if dataBase.check_user_by_chat_id(chat_id) == 0:
            currentState = None
        else:
            currentState = dataBase.get_state_by_chat_id(chat_id)

        if text=="/start":
            if dataBase.check_user_by_chat_id(chat_id) == 0:
                dataBase.add_user(chat_id, username)
                msg = "You are subcribed to Vaccine Updates! Thank you {}.\nYou can add your current state and city with the commands /addstate and /addcity".format(username)
                send_message(msg, chat_id)
            else:
                msg = "You are alreay subcribed to Vaccine Updates! Thank you {}.\nYou can update your current state and city with the commands /addstate and /addcity".format(username)
                send_message(msg, chat_id)
        elif text == "/addstate":
            keyboard = build_keyboard(states)
            send_message("Select a state", chat_id, keyboard)
        elif text in states:
            dataBase.set_state_by_chat_id(text, chat_id)
            send_message("State saved", chat_id) 
        elif text == "/addcity":
            if currentState != None:
                keyboard = build_keyboard(cities[currentState])
                send_message("Select a city", chat_id, keyboard)
            else:
                send_message("Select a state first /addstate", chat_id) 
        elif currentState != None and text in cities[currentState]:
            dataBase.set_city_by_chat_id(text, chat_id)
            send_message("City saved", chat_id) 
        else:
            send_message("Invalid command", chat_id) 

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    get_url(url)

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    dataBase = DBHelper()
    dataBase.setup()
    last_update_id = None
    while exit_event.is_set():
        print(last_update_id)
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates, dataBase)
        time.sleep(0.5)


@app.route('/API/publish', methods=['POST'])
def sendMessage():
    dataBaseMain = DBHelper()
    body = request.get_json()
    msg = "*--- Vaccine Available ---*\n\n"
    for index, item in enumerate(body['data'], start=1):
        msg = msg + str(index) + ". " + item['location'] + " (Count: " + item['count'] + "), " + item['city'] + "\n\n"
    #telegram_send.send(messages=[msg])
    for chat_id in dataBaseMain.get_all_chat_id_by_city(body['city']):
        send_message(msg,chat_id)
    return jsonify(
        status="OK",
        message="Information Published"
    )


@app.route('/API/notifyAdmin', methods=['POST'])
def sendExpMessage():
    telegram_send.send(messages=["Token Timeout! Login again."])
    return "OK"

if __name__ == '__main__':
    exit_event.set()
    chatbot = threading.Thread(target=main, args=())
    chatbot.daemon = True
    chatbot.start()
    try:
        app.run()
    except KeyboardInterrupt:
        exit_event.clear()
        chatbot.join()
    