import imaplib
import email
import os
import time
from email.header import decode_header
from google import genai
from pydantic import BaseModel

# --- CONFIGURATION ---
EMAIL_USER = "<YOUR_EMAIL>@gmail.com"
EMAIL_PASS = "xxxx xxxx xxxx xxxx"  # ⚠️ REMINDER: Revoke/Change this key!
GEMINI_KEY = "YOUR_GEMINI_API_KEY_HERE"  # ⚠️ REMINDER: Revoke/Change this key!
UID_FILE = "last_id.txt"

# --- HELPER FUNCTIONS ---
def get_last_seen_uid():
    if os.path.exists(UID_FILE):
        with open(UID_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_seen_uid(uid):
    with open(UID_FILE, "w") as f:
        f.write(str(uid))

class PhishingAnalysis(BaseModel):
    score: float
    is_phishing: bool
    reason: str

# --- INITIALIZATION ---
client = genai.Client(api_key=GEMINI_KEY)
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL_USER, EMAIL_PASS)

last_seen = get_last_seen_uid()

# If first time running, mark the current latest email as the starting point
if last_seen is None:
    mail.select("inbox")
    _, messages = mail.uid('search', None, "ALL")
    last_seen = messages[0].split()[-1].decode()
    save_last_seen_uid(last_seen)
    print(f"📡 Monitor started. Initialized at UID: {last_seen}")

# --- MAIN MONITORING LOOP ---
print("🕵️ Scanning for new phishing threats...")

while True:
    try:
        mail.select("inbox")
        # Search for all UIDs newer than our last seen
        search_criteria = f"UID {int(last_seen) + 1}:*"
        _, messages = mail.uid('search', None, search_criteria)
        new_uids = messages[0].split()

        for uid in new_uids:
            uid_str = uid.decode()
            _, data = mail.uid('fetch', uid_str, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            # Extract Subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            # Extract Plain Text Body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            # AI Analysis
            prompt = f"Analyze for phishing.\nSubject: {subject}\nBody: {body}"
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config={'response_mime_type': 'application/json', 'response_schema': PhishingAnalysis}
            )
            
            analysis = response.parsed
            
            # --- ONLY PRINT IF PHISHING ---
            if analysis.is_phishing:
                print(f"\n🚨 ALERT: Phishing Detected (UID: {uid_str})")
                print(f"Subject: {subject}")
                print(f"Score: {analysis.score} | Reason: {analysis.reason}")
            
            # Always update the tracker so we don't scan this email again
            save_last_seen_uid(uid_str)
            last_seen = uid_str

    except Exception as e:
        print(f"❌ Error: {e}. Reconnecting...")
        time.sleep(10)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)

    time.sleep(30) # Poll every 30 seconds













        
