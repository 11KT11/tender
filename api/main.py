import requests
import os
from datetime import datetime

def calculate_match(title, desc, cpv):
    score = 0
    title_desc = (title + " " + desc).lower()
    
    # Słowa kluczowe Semicon (Wagi)
    keywords = {
        'pcb': 20, 'smt': 20, 'montaż kontraktowy': 15,
        'laser': 20, 'ems': 20, 'elektronika': 10, 'tht': 15
    }
    
    for word, points in keywords.items():
        if word in title_desc:
            score += points

    # Kody CPV Semicon
    semicon_cpvs = ['31711100', '32422000', '38636100']
    if any(code in cpv for code in semicon_cpvs):
        score += 30

    return min(score, 100)

def handler(request):
    # 1. Pobieranie danych z API e-Zamówienia (przykład)
    # W 2026 używamy endpointu dla nowych ogłoszeń
    API_URL = "https://ezamowienia.gov.pl/api/v2/tenders/current"
    
    try:
        response = requests.get(API_URL, timeout=10)
        tenders = response.json().get('data', [])
        
        for t in tenders:
            match = calculate_match(t['title'], t.get('description', ''), t.get('cpv', ''))
            
            if match >= 50:
                # 2. Wysyłka PUSH przez ntfy.sh
                topic = "semicon_alerts_2026_twoj_kod"
                requests.post(f"https://ntfy.sh/{topic}",
                    data=f"Dopasowanie: {match}% - {t['title']}".encode('utf-8'),
                    headers={
                        "Title": "Semicon: Nowy Przetarg",
                        "Priority": "high" if match > 75 else "default",
                        "Click": t['url'],
                        "Tags": "factory,potted_plant"
                    })
        
        return {"statusCode": 200, "body": "OK"}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
