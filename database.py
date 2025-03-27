import sqlite3
import logging

def init_db():
    conn = sqlite3.connect('festival.db')
    c = conn.cursor()
    
    # Создаем таблицу для зрителей
    c.execute('''CREATE TABLE IF NOT EXISTS spectators
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  date TEXT,
                  family_size TEXT,
                  name_age TEXT,
                  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Создаем таблицу для участников
    c.execute('''CREATE TABLE IF NOT EXISTS participants
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  team_size INTEGER,
                  team_name TEXT,
                  location TEXT,
                  participants_info TEXT,
                  special_status TEXT,
                  phone TEXT,
                  accommodation TEXT,
                  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def add_spectator(user_id, date, family_size, name_age):
    try:
        conn = sqlite3.connect('festival.db')
        c = conn.cursor()
        c.execute('''INSERT INTO spectators (user_id, date, family_size, name_age)
                     VALUES (?, ?, ?, ?)''', (user_id, date, family_size, name_age))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error adding spectator: {e}")
        return False

def add_participant(user_id, team_size, team_name, location, participants_info, 
                   special_status, phone, accommodation):
    try:
        conn = sqlite3.connect('festival.db')
        c = conn.cursor()
        c.execute('''INSERT INTO participants 
                     (user_id, team_size, team_name, location, participants_info, 
                      special_status, phone, accommodation)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, team_size, team_name, location, participants_info,
                   special_status, phone, accommodation))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error adding participant: {e}")
        return False 