import os

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

import threading
import time
import sqlite3

import data
from data import get_db
import time

# ímport telebot
BOT_TOKEN = data.telegram_bot_token
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start", "help"])
def start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Aktuelle Decks anfordern", callback_data="get"))
    markup.add(InlineKeyboardButton("Abonnieren", callback_data="subscribe"))
    bot.reply_to(message, "Werkzeug für Chinesisch -> Anki", reply_markup=markup)

def draw_subscription_markup(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)

    for deck in data.get_available_decks():
        is_subscribed = is_subscribed_to_deck(chat_id, deck.id)
        button_text = "✔️" if is_subscribed else "⭕️"
        button_text += " " + deck.anki_name

        callback_data = "u " if is_subscribed else "s "
        callback_data += deck.internal_name

        markup.add(InlineKeyboardButton(button_text, callback_data=callback_data))

    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("s "):
        print(f"message_id={call.message.id}")
        subscribe(call.from_user.id, call.from_user.first_name, call.from_user.last_name, call.data.split()[1])

        new_markup = draw_subscription_markup(call.from_user.id)
        if new_markup != call.message.reply_markup:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=new_markup)
    elif call.data.startswith("u "):
        print(f"message_id={call.message.id}")
        unsubscribe(call.from_user.id, call.from_user.first_name, call.from_user.last_name, call.data.split()[1])

        new_markup = draw_subscription_markup(call.from_user.id)
        if new_markup != call.message.reply_markup:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=new_markup)
    elif call.data == "get":
        send_get_message(call.from_user.id)
    elif call.data == "subscribe":
        subscribe_message(call.from_user.id)

    bot.answer_callback_query(call.id)

def subscribe(user_id, first_name, last_name, deck_internal_name):
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT id FROM decks WHERE internal_name = ?", (deck_internal_name,))
    deck_result = cur.fetchone()

    if deck_result:
        deck_id = deck_result[0]
        cur.execute("INSERT INTO telegram_subscribers (chat_id, first_name, last_name) VALUES (?, ?, ?) ON CONFLICT(chat_id) DO NOTHING", (user_id, first_name, last_name))
        cur.execute("INSERT INTO telegram_subscribed_to (chat_id, deck_id) VALUES (?, ?) ON CONFLICT DO NOTHING", (user_id,deck_id))
        con.commit()

def subscribe_message(chat_id):
    bot.send_message(chat_id, "Bitte klicke auf die Buttons um die Ankidecks zu abonnieren.", reply_markup=draw_subscription_markup(chat_id))

def unsubscribe(user_id, first_name, last_name, deck_internal_name):
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT id FROM decks WHERE internal_name = ?", (deck_internal_name,))
    deck_result = cur.fetchone()

    if deck_result:
        deck_id = deck_result[0]
        cur.execute("INSERT INTO telegram_subscribers (chat_id, first_name, last_name) VALUES (?, ?, ?) ON CONFLICT(chat_id) DO NOTHING", (user_id, first_name, last_name))
        cur.execute("DELETE FROM telegram_subscribed_to WHERE chat_id = ? AND deck_id = ?", (user_id, deck_id))
        con.commit()

@bot.message_handler(commands=["subscribe"])
def subscribe_command(message):
    subscribe_message(message.from_user.id)

@bot.message_handler(commands=["stop", "unsubscribe"])
def unsubscribe_command(message):
    unsubscribe(message.from_user.id)
    bot.reply_to(message, "Du hast deabonniert.")

@bot.message_handler(commands=["get"])
def get_command(message):
    send_get_message(message.from_user.id)

def get_subscriber_from_chat_id(chat_id):
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM telegram_subscribers WHERE chat_id = ?", (chat_id,))
    return cur.fetchone()

def get_subscribers():
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM telegram_subscribers")
    return cur.fetchall()

anki_decks = ["Chinesisch IV.apkg", "Hanzi IV.apkg"]

def send_get_message(user_id):
    for anki_deck in anki_decks:
        doc = open(anki_deck, 'rb')
        bot.send_document(user_id, doc)

def is_subscribed_to_deck(chat_id, deck_id):
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM telegram_subscribed_to WHERE chat_id = ? AND deck_id = ?", (chat_id, deck_id))
    return bool(cur.fetchone())

def send_update_message(decks):
    subscribers = get_subscribers()

    for subscriber in subscribers:
        for deck in decks:
            if is_subscribed_to_deck(subscriber.chat_id, deck.id):
                bot.send_message(subscriber.chat_id, "Es gibt neue Updates bei den von dir abonnierten Ankidecks!")
                time.sleep(0.1)
                break

    for deck in decks:
        deck_file = open(f"{deck.anki_name}.apkg", "rb")

        for subscriber in subscribers:
            if is_subscribed_to_deck(subscriber.chat_id, deck.id):
                bot.send_document(subscriber.chat_id, deck_file)
                time.sleep(0.1)

if __name__ == "__main__":
    # send_startup_message()
    bot.infinity_polling()

