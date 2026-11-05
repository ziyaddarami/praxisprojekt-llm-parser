# ============================================================
# Praxisprojekt: LLM-basiertes Dokument-Parsing für RAG
# Autor: Ziyad Darami | Matrikelnummer: 11240956 | TH Köln
# Ziel: Testen ob KI Webseiten erschließen kann, die der
#       BOTSchafft-Parser NICHT lesen konnte
# ============================================================

from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import time
import openpyxl
import json
from datetime import datetime

# --- KI-Verbindung zur Ki:connect API der TH Köln ---
client = OpenAI(
    api_key="6acb7a1b521baf09c09bdcd1:5jEhC6/xyuSWdP06UhH6Qnh5AOMAmKscOEFsAWI0pSc=",
    base_url="https://chat.kiconnect.nrw/api/v1"
)

# --- Excel-Datei einlesen: 44 URLs die BOTSchafft nicht lesen konnte ---
wb = openpyxl.load_workbook(r"C:\Users\ziyad\OneDrive\Bureau\Liste_Datenquellen_Botschafft_1.xlsx")
ws = wb.active

urls_nein = []
for row in ws.iter_rows(min_row=2, values_only=True):
    # Spalte 6 (index 5) = Einlesbar mit BOTSchafft? → Nein
    # Spalte 4 (index 3) = Typ → WEB
    # Spalte 5 (index 4) = URL
    if row[5] == 'Nein' and row[3] == 'WEB' and row[4]:
        urls_nein.append(row[4])

print(f"Gefundene Test-URLs: {len(urls_nein)}")

# --- Browser-Header damit Webseiten uns nicht blockieren ---
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# --- Bewertungsfunktion ---
def bewerte_ergebnis(text_laenge, zusammenfassung):
    """
    Kriterien:
    KEIN_TEXT    = Webseite leer oder nicht erreichbar (unter 100 Zeichen)
    ZU_WENIG     = Zu wenig Text für sinnvolle Zusammenfassung
    KEIN_INHALT  = KI findet keinen relevanten Inhalt
    ERFOLGREICH  = Text extrahiert + gute KI-Zusammenfassung
    """
    if text_laenge < 100:
        return "KEIN_TEXT"
    if len(zusammenfassung) < 50:
        return "ZU_WENIG"
    if any(phrase in zusammenfassung.lower() for phrase in [
        "kein inhalt", "keine information", "not found", "fehler", "error"
    ]):
        return "KEIN_INHALT"
    return "ERFOLGREICH"

# --- Hauptschleife: alle 44 URLs testen ---
ergebnisse = []

for i, url in enumerate(urls_nein):
    print(f"\n[{i+1}/44] {url[:70]}")

    ergebnis = {
        "nummer": i + 1,
        "url": url,
        "text_laenge": 0,
        "zusammenfassung": "",
        "bewertung": "",
        "zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    try:
        # Schritt 1: Webseite herunterladen und Text extrahieren
        response_web = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response_web.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        ergebnis["text_laenge"] = len(text)
        print(f"   → {len(text)} Zeichen extrahiert")

        # Schritt 2: Text an KI schicken und zusammenfassen lassen
        response_ki = client.chat.completions.create(
            model="mistralai-mistral-small-4-119b-2603",
            messages=[{
                "role": "user",
                "content": (
                    f"Fasse den folgenden Webseiteninhalt in 3-5 Sätzen zusammen. "
                    f"Wenn kein sinnvoller Inhalt vorhanden ist, schreibe 'Kein relevanter Inhalt'.\n\n"
                    f"{text[:3000]}"
                )
            }]
        )
        zusammenfassung = response_ki.choices[0].message.content
        ergebnis["zusammenfassung"] = zusammenfassung
        print(f"   → KI: {zusammenfassung[:80]}...")

    except Exception as e:
        ergebnis["zusammenfassung"] = f"Fehler: {str(e)}"
        print(f"   → FEHLER: {e}")

    # Schritt 3: Ergebnis bewerten
    ergebnis["bewertung"] = bewerte_ergebnis(
        ergebnis["text_laenge"],
        ergebnis["zusammenfassung"]
    )
    print(f"   → Bewertung: {ergebnis['bewertung']}")
    ergebnisse.append(ergebnis)

    # Pause damit wir nicht geblockt werden
    time.sleep(2)

# --- Ergebnisse als JSON speichern ---
with open(r"C:\Users\ziyad\OneDrive\Bureau\ergebnisse.json", "w", encoding="utf-8") as f:
    json.dump(ergebnisse, f, ensure_ascii=False, indent=2)

# --- Auswertung anzeigen ---
erfolgreich = sum(1 for e in ergebnisse if e["bewertung"] == "ERFOLGREICH")
kein_text   = sum(1 for e in ergebnisse if e["bewertung"] == "KEIN_TEXT")
zu_wenig    = sum(1 for e in ergebnisse if e["bewertung"] == "ZU_WENIG")
kein_inhalt = sum(1 for e in ergebnisse if e["bewertung"] == "KEIN_INHALT")
gesamt      = len(ergebnisse)

print("\n" + "="*50)
print("AUSWERTUNG")
print("="*50)
print(f"Gesamt:          {gesamt} URLs")
print(f"✅ ERFOLGREICH:  {erfolgreich} ({erfolgreich/gesamt*100:.1f}%)")
print(f"❌ KEIN_TEXT:    {kein_text} ({kein_text/gesamt*100:.1f}%)")
print(f"⚠️  ZU_WENIG:    {zu_wenig} ({zu_wenig/gesamt*100:.1f}%)")
print(f"⚠️  KEIN_INHALT: {kein_inhalt} ({kein_inhalt/gesamt*100:.1f}%)")
print(f"\n✅ Gespeichert: ergebnisse.json")