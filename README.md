# quo-vadis-democracy-interactive-questionnaire

Minimal Streamlit MVP for the "Digital Agora" project.

## What this version does

- Starts successfully on Streamlit Cloud
- Tries to connect to Google Sheets
- Accepts one text response + one threat slider response
- Writes rows to a `responses` worksheet
- Shows recent rows as a smoke test

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit secrets (example)

Set your credentials in Streamlit secrets and configure your gsheets connection.
The exact values depend on your Google service account setup.