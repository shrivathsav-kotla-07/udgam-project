import os
import spacy
import pandas as pd
import pywhatkit
import speech_recognition as sr
from fuzzywuzzy import process

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Load contacts from CSV
def load_contacts(csv_file):
    if not os.path.exists(csv_file):  
        return {}
    
    try:
        contacts_df = pd.read_csv(csv_file, dtype=str)
        contacts_df.columns = contacts_df.columns.str.strip()

        if "Name" not in contacts_df or "Phone" not in contacts_df:
            return {}

        contacts_df["Phone"] = contacts_df["Phone"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        contacts_df["Phone"] = contacts_df["Phone"].apply(lambda x: "+" + x if not x.startswith("+") else x)

        return dict(zip(contacts_df["Name"].str.lower(), contacts_df["Phone"]))
    
    except Exception:
        return {}

# Load contacts once to avoid reloading each time
contacts = load_contacts("contacts.csv")

# Extract contact and message from user input
def extract_contact_and_message(user_input):
    contact_name, message = None, None
    if "send" in user_input.lower() and "to" in user_input.lower():
        contact_start = user_input.lower().find("to") + 3  
        contact_name = user_input[contact_start:user_input.lower().find("saying")].strip()
        
        message_start = user_input.lower().find("saying") + 7  
        message = user_input[message_start:].strip()

    return contact_name, message

# Find best matching contact
def find_best_match(contact_name):
    if not contacts:
        return None
    best_match, score = process.extractOne(contact_name.lower(), contacts.keys()) if contacts else (None, 0)
    return contacts.get(best_match) if score > 70 else None

# Send message via WhatsApp
def send_whatsapp_message(contact_name, message):
    contact_number = find_best_match(contact_name)
    if contact_number:
        pywhatkit.sendwhatmsg_instantly(str(contact_number), message, wait_time=10)
        return f"Message sent to {contact_name} ({contact_number})."
    else:
        return f"Contact '{contact_name}' not found."

# Main function for chatbot to call
def whatsapp_message_assistant(user_input, use_voice=False):
    """Handles WhatsApp messaging via text or voice input."""
    
    if use_voice:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                user_input = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return "Could not understand the audio."
            except sr.RequestError:
                return "Could not connect to speech recognition service."

    contact_name, message = extract_contact_and_message(user_input)
    
    if not contact_name or not message:
        return "Could not extract contact or message properly."
    
    return send_whatsapp_message(contact_name, message)