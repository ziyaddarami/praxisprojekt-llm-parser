import json
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment

# JSON einlesen
with open(r"C:\Users\ziyad\OneDrive\Bureau\ergebnisse.json", "r", encoding="utf-8") as f:
    ergebnisse = json.load(f)

# Neue Excel-Datei erstellen
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Ergebnisse"

# Kopfzeile
ws.append(["Nr.", "URL", "Zeichen", "KI-Zusammenfassung", "Bewertung", "Zeitstempel"])

# Kopfzeile blau einfärben
for col in range(1, 7):
    zelle = ws.cell(row=1, column=col)
    zelle.fill = PatternFill("solid", fgColor="2D5A8E")
    zelle.font = Font(color="FFFFFF", bold=True)
    zelle.alignment = Alignment(horizontal="center")

# Farben je nach Bewertung
farben = {
    "ERFOLGREICH": "C6EFCE",  # Grün
    "KEIN_TEXT":   "FFCCCC",  # Rot
    "ZU_WENIG":    "FFEB9C",  # Gelb
    "KEIN_INHALT": "FFEB9C",  # Gelb
}

# Daten einfügen
for e in ergebnisse:
    ws.append([
        e["nummer"],
        e["url"],
        e["text_laenge"],
        e["zusammenfassung"],
        e["bewertung"],
        e["zeitstempel"]
    ])
    farbe = farben.get(e["bewertung"], "FFFFFF")
    for col in range(1, 7):
        ws.cell(row=e["nummer"]+1, column=col).fill = PatternFill("solid", fgColor=farbe)

# Spaltenbreiten
ws.column_dimensions["A"].width = 5
ws.column_dimensions["B"].width = 50
ws.column_dimensions["C"].width = 10
ws.column_dimensions["D"].width = 60
ws.column_dimensions["E"].width = 15
ws.column_dimensions["F"].width = 18

# Speichern
wb.save(r"C:\Users\ziyad\OneDrive\Bureau\ergebnisse_llm.xlsx")
print("✅ Excel gespeichert: ergebnisse_llm.xlsx")