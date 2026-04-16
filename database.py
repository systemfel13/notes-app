import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.db")

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            note_id INTEGER PRIMARY KEY,
            note_title TEXT NOT NULL,
            note_text TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def get_all_notes():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    # Newest notes first — sort by ID from highest to lowest
    cursor.execute("SELECT note_id, note_title FROM notes ORDER BY note_id DESC")
    notes = cursor.fetchall()
    connection.close()
    return notes

def get_note(note_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notes WHERE note_id = ?", (note_id,))
    note = cursor.fetchone()
    connection.close()
    return note

def create_note(title, text):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO notes (note_title, note_text) VALUES (?, ?)", (title, text))
    note_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return note_id

def update_note(note_id, title, text):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("UPDATE notes SET note_title = ?, note_text = ? WHERE note_id = ?", (title, text, note_id))
    connection.commit()
    connection.close()

def delete_note(note_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM notes WHERE note_id = ?", (note_id,))
    connection.commit()
    connection.close()