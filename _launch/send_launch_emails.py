"""
Nimbus-24 Launch Notification Sender
=====================================
Sends launch notification emails to waitlist subscribers.

SETUP:
  1. Export emails from Formspree (see launch-guide.md)
  2. Save as waitlist_emails.csv with one column: "email"
  3. Set your Resend API key as environment variable
  4. Run: python send_launch_emails.py

REQUIREMENTS:
  pip install resend
"""

import resend
import csv
import os
import time
import sys
from datetime import datetime

# ── CONFIG ──
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_YOUR_API_KEY_HERE")
FROM_EMAIL = "Nimbus-24 <launch@nimbus-24.com>"  # Must be a verified domain in Resend
CSV_FILE = "waitlist_emails.csv"
DELAY_BETWEEN_EMAILS = 0.5  # seconds, to avoid rate limits

# ── EMAIL CONTENT ──
SUBJECT = "🚀 Nimbus-24 is live — the enchantment begins"

HTML_BODY = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: Georgia, 'Times New Roman', serif; background: #faf7f2; margin: 0; padding: 0; }
  .wrapper { max-width: 560px; margin: 0 auto; padding: 40px 28px; }
  .header { text-align: center; margin-bottom: 32px; }
  .logo { font-family: Georgia, serif; font-size: 24px; font-weight: bold; color: #1a2e1a; }
  .logo span { color: #2d7a4f; }
  h1 { font-size: 28px; color: #1a2e1a; line-height: 1.3; margin-bottom: 16px; }
  p { font-size: 16px; color: #4a6355; line-height: 1.7; margin-bottom: 16px; }
  .divider { border: none; border-top: 1px solid #ddd5c4; margin: 28px 0; }
  .product { background: #fff; border: 1px solid #ddd5c4; border-radius: 12px; padding: 24px; margin-bottom: 16px; }
  .product h3 { font-size: 18px; color: #1a2e1a; margin-bottom: 4px; }
  .product .tag { font-size: 11px; color: #8aaa95; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
  .product p { font-size: 14px; margin-bottom: 12px; }
  .product a { display: inline-block; font-size: 14px; color: #2d7a4f; font-weight: bold; text-decoration: none; }
  .cta-block { background: #1a2e1a; border-radius: 12px; padding: 32px; text-align: center; margin: 28px 0; }
  .cta-block h2 { font-size: 22px; color: #fff; margin-bottom: 8px; }
  .cta-block p { color: rgba(255,255,255,0.5); font-size: 14px; margin-bottom: 20px; }
  .cta-btn { display: inline-block; background: #2d7a4f; color: #fff; font-size: 15px; font-weight: bold; padding: 14px 32px; border-radius: 8px; text-decoration: none; }
  .footer { text-align: center; font-size: 12px; color: #8aaa95; margin-top: 32px; line-height: 1.6; }
  .footer a { color: #2d7a4f; text-decoration: none; }
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <div class="logo">🌿 Nimbus<span>-24</span></div>
  </div>

  <h1>The wait is over.<br>Nimbus-24 is live. 🚀</h1>
  
  <p>
    You signed up to be the first to know — and here we are. 
    Two AI-powered products, built at the intersection of technology and human care, 
    are now live and ready for you to explore.
  </p>

  <hr class="divider">

  <div class="product">
    <h3>🧠 Proche Aidant</h3>
    <div class="tag">Healthcare AI · Live Now</div>
    <p>
      A conversational AI companion for people in the early stages of dementia 
      and their caregivers. It remembers who you are, tracks medications, 
      and responds when you're in distress.
    </p>
    <a href="https://nimbus-24.com/proche-aidant.html">Explore Proche Aidant →</a>
  </div>

  <div class="product">
    <h3>🌿 Lektes</h3>
    <div class="tag">AI Recruitment Screening · Live Now</div>
    <p>
      From the Greek <em>lektós</em> — chosen, selected. Paste a job description, upload CVs, 
      and get a ranked shortlist with scores, skills analysis, and tailored interview questions — in under 2 minutes.
    </p>
    <a href="https://nimbus-24.com/lektes.html">Explore Lektes →</a>
  </div>

  <div class="cta-block">
    <h2>Visit the new site</h2>
    <p>Everything is live — explore at your own pace</p>
    <a href="https://nimbus-24.com" class="cta-btn">Open nimbus-24.com →</a>
  </div>

  <p style="font-size: 14px; color: #8aaa95; text-align: center;">
    Thank you for believing in us before you could see what we were building. 
    That trust means everything. ✨
  </p>

  <div class="footer">
    <p>
      <a href="https://nimbus-24.com">nimbus-24.com</a><br>
      You received this because you signed up for launch notifications.<br>
      This is the only email we'll send — no spam, ever. Mischief managed. 🪄
    </p>
  </div>

</div>
</body>
</html>
"""

TEXT_BODY = """
The wait is over — Nimbus-24 is live! 🚀

You signed up to be the first to know, and here we are. Two AI-powered products are now live:

🧠 PROCHE AIDANT — Healthcare AI
A conversational AI companion for people in the early stages of dementia and their caregivers.
→ https://nimbus-24.com/proche-aidant.html

🌿 LEKTES — AI Recruitment Screening
From the Greek lektós — chosen, selected.
Paste a job description, upload CVs, get a ranked shortlist in under 2 minutes.
→ https://nimbus-24.com/lektes.html

Visit the new site: https://nimbus-24.com

Thank you for believing in us before you could see what we were building. ✨

— Nimbus-24
nimbus-24.com

You received this because you signed up for launch notifications. 
This is the only email we'll send — no spam, ever.
"""


def load_emails(csv_path):
    """Load email addresses from CSV file."""
    emails = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get("email", "").strip()
            if email and "@" in email:
                emails.append(email)
    return emails


def send_notification(email_address):
    """Send launch notification to a single email."""
    try:
        result = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [email_address],
            "subject": SUBJECT,
            "html": HTML_BODY,
            "text": TEXT_BODY,
        })
        return True, result
    except Exception as e:
        return False, str(e)


def main():
    # Set API key
    resend.api_key = RESEND_API_KEY

    if RESEND_API_KEY == "re_YOUR_API_KEY_HERE":
        print("❌ ERROR: Set your Resend API key!")
        print("   export RESEND_API_KEY='re_your_actual_key'")
        sys.exit(1)

    # Load emails
    if not os.path.exists(CSV_FILE):
        print(f"❌ ERROR: {CSV_FILE} not found!")
        print("   Export your Formspree submissions and save as waitlist_emails.csv")
        print('   Format: CSV with header row containing "email" column')
        sys.exit(1)

    emails = load_emails(CSV_FILE)
    print(f"📧 Found {len(emails)} email(s) to notify")
    print(f"⏰ Starting at {datetime.now().strftime('%H:%M:%S')}")
    print("─" * 48)

    # Send emails
    sent = 0
    failed = 0

    for i, email in enumerate(emails, 1):
        success, result = send_notification(email)

        if success:
            sent += 1
            print(f"  ✅ [{i}/{len(emails)}] {email}")
        else:
            failed += 1
            print(f"  ❌ [{i}/{len(emails)}] {email} — {result}")

        # Rate limiting
        if i < len(emails):
            time.sleep(DELAY_BETWEEN_EMAILS)

    # Summary
    print("─" * 48)
    print(f"🎉 Done! Sent: {sent} | Failed: {failed} | Total: {len(emails)}")
    print(f"⏰ Finished at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
