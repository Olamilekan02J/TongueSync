import streamlit as st
import speech_recognition as sr
import pyttsx3
import time
import pandas as pd
import nltk
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity      
import warnings
warnings.filterwarnings('ignore')
lemmatizer = nltk.stem.WordNetLemmatizer()
import speech_recognition as sr
from googletrans import Translator
import sqlite3

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT,
            detected_language TEXT,
            target_language TEXT,
            translated_text TEXT,
            voice BLOB
        )
    ''')
    conn.commit()

def insert_translation(conn, original_text, detected_language, target_language, translated_text, voice):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO translations (
            original_text, detected_language, target_language, translated_text, voice
        ) VALUES (?, ?, ?, ?, ?)
    ''', (original_text, detected_language, target_language, translated_text, voice))
    conn.commit()

def recognize_and_translate():
    recognizer = sr.Recognizer()
    translator = Translator()
    
    conn = sqlite3.connect('translations.db')
    create_table(conn)

    try:
        with sr.Microphone() as source:
            print("Please speak:")
            audio = recognizer.listen(source, timeout=5)

            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            print(f"You said: {query}")

            detected_language = translator.detect(query).lang
            print(f"Detected Language: {detected_language}")

            reply = input("Is this correct? (yes/no): ").lower()

            if reply == 'yes':
                target_language = input("Enter the target language code (e.g., fr for French): ")
                translation = translator.translate(query, src=detected_language, dest=target_language).text
                print(f"Translated to {target_language}: {translation}")

                insert_translation(conn, query, detected_language, target_language, translation, audio.get_raw_data())
            else:
                print("Sorry, could not understand audio. Try again")

    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
    except sr.RequestError as e:
        print(f"Speech recognition request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    recognize_and_translate()
