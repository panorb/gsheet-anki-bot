import sqlite3
import tomllib
from collections import namedtuple

def namedtuple_factory(cursor, row):
    """Returns sqlite rows as named tuples."""
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)

def get_db():
    con = sqlite3.connect("cache.db",
                          detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    con.row_factory = namedtuple_factory
    return con

def table_exists(name):
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT name from sqlite_master WHERE type = ? AND name = ?", ("table", name))
    return bool(cur.fetchone())

def _drop_decks_table():
    con = get_db()
    cur = con.cursor()
    cur.execute("DROP TABLE decks")

def _create_deck(cur, deck_id, deck_type, internal_name, sheet_name, anki_name):
    cur.execute("INSERT INTO decks (id, deck_type, internal_name, sheet_name, anki_name) VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING", (deck_id, deck_type, internal_name, sheet_name, anki_name))

def get_available_decks():
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT id, deck_type, internal_name, sheet_name, anki_name, state_sheet_hash FROM decks")
    return cur.fetchall()

def _init_db():
    con = get_db()
    cur = con.cursor()

    if not table_exists("decks"):
        cur.execute("CREATE TABLE IF NOT EXISTS decks (`id` VARCHAR(20) NOT NULL PRIMARY KEY, `deck_type` VARCHAR(20) CHECK(deck_type in ('vocab', 'hanzi') ) NOT NULL, `internal_name` VARCHAR(20) NOT NULL UNIQUE, `sheet_name` VARCHAR(50) NOT NULL UNIQUE, `anki_name` VARCHAR(50) NOT NULL UNIQUE, `state_sheet_hash` VARCHAR(70))")
        _create_deck(cur, "1665304798265", "vocab", "chinese1", "Vokabeln I", "Chinesisch I")
        _create_deck(cur, "1683374545741", "vocab", "chinese2", "Vokabeln II", "Chinesisch II")
        _create_deck(cur, "1697996748710", "vocab", "chinese3", "Vokabeln III", "Chinesisch III")
        _create_deck(cur, "1711962059715", "vocab", "chinese4", "Vokabeln IV", "Chinesisch IV")
        _create_deck(cur, "1701332896192", "hanzi", "hanzi3", "Hanzi III", "Hanzi III")
        _create_deck(cur, "1711962050728", "hanzi", "hanzi4", "Hanzi IV", "Hanzi IV")
        con.commit()

    if not table_exists("telegram_subscribers"):
        cur.execute("CREATE TABLE IF NOT EXISTS telegram_subscribers (`chat_id` VARCHAR(20) NOT NULL PRIMARY KEY, `first_name` VARCHAR(255), `last_name` VARCHAR(255))")
        con.commit()

    if not table_exists("telegram_subcribed_to"):
        cur.execute("CREATE TABLE IF NOT EXISTS telegram_subscribed_to (`chat_id` VARCHAR(20) NOT NULL, `deck_id` VARCHAR(20) NOT NULL, PRIMARY KEY (chat_id, deck_id))")

spreadsheet_id = ""
telegram_bot_token = ""

def _load_config():
    global telegram_bot_token
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        spreadsheet_id = data["spreadsheet_id"]
        telegram_bot_token = data["tokens"]["telegram"]

_load_config()
# _drop_decks_table()
_init_db()
