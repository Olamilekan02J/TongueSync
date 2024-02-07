import speech_recognition as sr
import pyttsx3
import time
import pandas as pd
import nltk
import random    
import warnings
warnings.filterwarnings('ignore')
lemmatizer = nltk.stem.WordNetLemmatizer()
import speech_recognition as sr
from googletrans import Translator
import sqlite3
import pyttsx3
import re

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

def speak_translated_audio_with_punctuation(text):
    text = re.sub(r'<.*?>', '', text)    #............ Remove potential HTML tags from the text
    engine = pyttsx3.init()     #............ Initialize the text-to-speech engine
    #..............Set properties (optional)............
    engine.setProperty('rate', 120)  # Adjust the speed of speech
    engine.setProperty('volume', 0.6)  # Adjust the volume (0.0 to 1.0)
    engine.say(text)    # ...........Speak out the translated text with punctuation
    engine.runAndWait()   #........... Wait for the speech to finish


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

                # Speak out the translated text with punctuation
                speak_translated_audio_with_punctuation(translation)

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
    # Call recognize_and_translate function
    recognize_and_translate()
