import sqlite3

def init_db():
    conn = sqlite3.connect('channels.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS channels (
                    user_id INTEGER PRIMARY KEY,
                    chat_id INTEGER
                )''')
    conn.commit()
    conn.close()

def set_channel(user_id: int, chat_id: int):
    conn = sqlite3.connect('channels.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO channels (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id))
    conn.commit()
    conn.close()

def get_channel(user_id: int):
    conn = sqlite3.connect('channels.db')
    c = conn.cursor()
    c.execute("SELECT chat_id FROM channels WHERE user_id = ?", (user_id, ))
    result = c.fetchone()
    conn.close()

    return result[0] if result else None