from openai import OpenAI
import requests
from bs4 import BeautifulSoup

client = OpenAI(
    api_key="6acb7a1b521baf09c09bdcd1:5jEhC6/xyuSWdP06UhH6Qnh5AOMAmKscOEFsAWI0pSc=",
    base_url="https://chat.kiconnect.nrw/api/v1"
)

url = "https://www.gesetze-im-internet.de/burlg/__3.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

response_web = requests.get(url, headers=headers)
soup = BeautifulSoup(response_web.text, "html.parser")
text = soup.get_text(separator="\n", strip=True)

print(f"Seite geladen: {len(text)} Zeichen")
print(text[:500])
response = client.chat.completions.create(
    model="mistralai-mistral-small-4-119b-2603",
    messages=[
        {"role": "user", "content": f"Fasse den folgenden Gesetzestext kurz zusammen:\n\n{text}"}
    ]
)

print("\n--- LLM Antwort ---")
print(response.choices[0].message.content)