# Phishing Detection Tool

## Prerequisites

Before running this script, you need to have Python installed on your system. You will also need to install the required Python libraries.

You can install the necessary libraries using pip:

```bash
pip install google-generativeai pydantic
```

## Configuration

You need to configure the script with your email credentials and your Gemini API key. Open the `6_phishing_detection_tool.py` file and modify the following lines:

```python
# --- CONFIGURATION ---
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_app_password"  # ⚠️ REMINDER: Use an App Password for security
GEMINI_KEY = "your_gemini_api_key"
```

**Important:** For security reasons, it is highly recommended to use a [Google App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## How to Run

1.  Make sure you have completed the [Prerequisites](#prerequisites) and [Configuration](#configuration) steps.
2.  Open a terminal or command prompt.
3.  Navigate to the directory where the script is located.
4.  Run the script using the following command:

```bash
python 6_phishing_detection_tool.py
```

The script will start monitoring your inbox. It will check for new emails every 30 seconds.

## How it Works

-   The script connects to the specified Gmail account and selects the inbox.
-   It continuously scans for new emails that have arrived since the last check.
-   For each new email, it extracts the subject and the plain text body.
-   It sends the extracted text to the Gemini API for analysis.
-   The AI returns a phishing score, a boolean indicating if it's phishing, and a reason for its conclusion.
-   If the `is_phishing` flag is true, an alert is printed to the console with the email's subject, the phishing score, and the reason.
-   The script keeps track of the last email it processed to avoid analyzing the same email multiple times.
