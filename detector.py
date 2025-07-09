import requests
import json
import re
import os
# Lire le fichier de facture

def sendPrompt():
    with open("ocr_results.txt", "r", encoding="utf-8") as f:
        contenu_fichier = f.read()
    
    # Prompt structuré
    prompt = f"""
    Tu es un assistant comptable intelligent. Tu vas recevoir un texte brut issu d’un OCR d’une **facture ou note de frais**, souvent ligne à ligne.
    
    Ta mission est de structurer ce texte en **informations comptables fiables**, **sans calculer ni compléter des données manquantes**.
    
    Tu dois seulement retourner un JSON, qui doit pouvoir être utilisé comme tel directement. Je ne veux pas 
    ---
    
    1. Analyse et extraction :
    
    - Détecte le **type de dépense** (ex : "restaurant", "hôtel", "carburant", etc.).
    - Extrait **uniquement les montants exactement présents dans le texte** :
      - `montant_ht` : total HT (si affiché). Cherche la ligne "TOTAL HT" ou similaire.
      - `montant_ttc` : total TTC (si affiché). Cherche la ligne "TOTAL TTC" ou similaire.
      - `tva_total` : somme de **toutes les lignes de TVA visibles et explicitement identifiées comme TVA**.
      - `taux_tva` : tous les taux de TVA visibles (ex : [10.0, 20.0]).
      - `ventilation_tva` : liste détaillée des couples HT + TVA. **Associe un montant HT à un taux de TVA et son montant TVA si ces trois informations (taux, HT, montant TVA) apparaissent ensemble ou très proches dans le texte, par exemple sur des lignes consécutives ou la même ligne**.
        - Pour chaque taux de TVA (ex: 10.0%, 20.0%), cherche le montant HT associé et le montant de TVA correspondant.
    
     Si le montant n’est **pas strictement écrit dans le texte**, NE LE FOURNIS PAS. NE FAIS JAMAIS DE CALCUL.
    Toute tentative de deviner, reconstituer ou additionner entraînera une erreur.
    
    
    **Exemple de ventilation (si le texte contient "TVA (10.0%) - HT 180.00 - TVA 18.00" ou "HT 180.00 / TVA 10% / 18.00€"):**
    ```json
    "ventilation_tva": [
      {{
        "taux": 10.0,
        "montant_ht": 180.00,
        "montant_tva": 18.00
      }}
    ]
    
    Si les informations sont présentées comme:
    Ligne 1: TVA (10.0%)
    Ligne 2: HT 180.00
    Ligne 3: 18.00 EUR
    
    Alors la ventilation doit se faire si tu peux associer ces 3 éléments.
    
    Si aucune ligne ne donne explicitement le montant de tva total a payé, alors tva_total peut (et seulement dans ce cas ci) 
    être calculé en additionant les tva de ta ventilation
    
    Comptabilisation :
    
    Si identifiable, donne un compte comptable probable (ex : 606300, 625100). Sinon, mets null. Pour un restaurant, le compte est généralement 625100.
    
    Format de réponse JSON :
    
    '''json
    
    {{
      "type_depense": "string",
      "montant_ht": float,
      "tva_total": float,
      "taux_tva": [float],
      "montant_ttc": float,
      "compte_comptable": int | null,
      "ventilation_tva": [
        {{
          "taux": float,
          "montant_ht": float,
          "montant_tva": float
        }}
      ]
    }}
    
    Voici un exemple d’analyse correcte :
    
    Texte brut :
    Ticket
    
    Le
    
    Restaurant
    
    Tiller
    
    42
    
    rue
    
    Louts
    
    Blanc
    
    75010
    
    Paris
    
    Siret:
    
    0123456789
    
    2017-07-05 17:41:49
    
    Date
    
    1mpression:
    
    2017-07-05 16:53:00
    
    Ouverture:
    
    2017-07-05 17:41:49
    
    Cloture:
    
    Commandes: 6
    
    Clients: 10
    
    Ticket
    
    moyen: 25.70 EUR
    
    1
    
    AMEX
    
    12.00
    
    EUR
    
    4
    
    Carte bancaire
    
    136.00
    
    EUR
    
    2
    
    Espèces
    
    85.00
    
    EUR
    
    1
    
    Ticket restaurant
    
    24.00
    
    EUR
    
    TVA (10.0%)
    
    180.00
    
    18.00
    
    EUR
    
    49.17
    
    9.83 EUR
    
    TVA (20.0%)
    
    229.17 EUR
    
    TOTAL HT
    
    TOTAL
    
    TTC
    
    257.00
    
    EUR
    
    TOTAL Remises & Offerts
    
    0.00
    
    EUR
    
    TOTAL Annulations
    
    0.00
    
    EUR
    
    Fond de
    
    caisse
    
    initial
    
    100.00 EUR
    
    Fond de
    
    caisse final
    
    185.00 EUR
    
    Solde total des comptes clients
    
    0.00 EUR
     
    Résultat attendu :
    {{
    
      "type_depense": "restaurant",
    
      "montant_ht": 257.00,
    
      "tva_total": 27.83,
    
      "taux_tva": [10.0, 20.0],
    
      "montant_ttc": 284.83,
    
      "compte_comptable": 625100,
    
      "ventilation_tva": [
    
        {{
    
          "taux": 10.0,
    
          "montant_ht": 180.00,
    
          "montant_tva": 18.00
    
        }},
    
        {{
    
          "taux": 20.0,
    
          "montant_ht": 49.17,
    
          "montant_tva": 9.83
    
        }}
    
      ]
    
    }}
    
     
    
    autre exemple :
     
    Texte OCR :
    
    
    
    MARKET COUPVRAY
    
    Tel : 0164631166
    
    Lundi au Samedi de 8h30 à 20H00
    
    MoquoDimanche de 9H00 à 12H45
    
    QTE x P.U.
    
    HONTANT TTC:
    
    TUA DESCRIPTION
    
    ISESEHL
    
    6.12€
    
    6 *EAU CRESTALINE
    
    6 × 1.02€
    
    6.12€
    
    TOTAL ALIMENTAIRE
    
    1.99€
    
    7
    
    PAIC DEGR 500 ML
    
    1.99€
    
    TOTAL BEAUTE / SANTE / HYGIENE
    
    5.00€
    
    ARTICLES A 5 EURO
    
    5.00€
    
    TOTAL NON ALIMENTAIRE
    
    13.11€
    
    Sous-TOTAL.
    
    0080
    
    fonnée fournisse
    
    TOTAL A PAYER
    
    13.11€
    
    8 ARTICLE(S)
    
    asin de LOGNES
    
    EUR
    
    13.11€
    
    CB EMV SANS CONTACT
    
    000800
    
    TUA.
    
    Hors Taxe
    
    Taux
    
    hées (donn
    
    5.80
    
    6> 5.50
    
    0.32
    
    5.83
    
    7>20.00
    
    1.16
    
    au magasi
    
    11.63
    
    Totaux:
    
    1.48
    
    01/08/2022
    
    14:11:01
    
    7776
    
    0115
    
    010
    
    000461
    
    tach
    
    
     
    Réponse attendue :
    
    ```json
    
    {{
    
      "type_depense": "alimentaire",
    
      "montant_ht": 11.63,
    
      "tva_total": 1.48,
    
      "taux_tva": [5.5, 20.0],
    
      "montant_ttc": 13.11,
    
      "compte_comptable": 606300,
    
      "ventilation_tva": [
    
        {{
    
          "taux": 5.5,
    
          "montant_ht": 5.80,
    
          "montant_tva": 0.32
    
        }},
    
        {{
    
          "taux": 20.0,
    
          "montant_ht": 5.83,
    
          "montant_tva": 1.16
    
        }}
    
      ]
    
    }}
     
    Encore une fois, je ne veux pas de texte autour de ta réponse, qui ne doit seulement être du json
    
    Texte : 
        
    \"\"\"
    {contenu_fichier}
    \"\"\"
    """
    
    # Requête à Ollama
    OLLAMA_API = os.getenv("OLLAMA_API", "http://ollama:11434")
    
    response = requests.post(
        f"{OLLAMA_API}/api/generate",
        json={
            "model": "gemma3",  # ou un autre modèle que tu veux charger
            "prompt": f"{prompt}",
            "stream": False
        }
    )
    

    # Nettoyage brut
    output = response.json()["response"].strip()
    
    # Supprimer les ```json ou ``` si présents (merci gpt pour le debug)
    output = re.sub(r"^```(json)?", "", output)
    output = re.sub(r"```$", "", output)
    output = output.strip()
    
    # Essai de parsing JSON
    try:
        data = json.loads(output)
        with open("facture_analysee.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(" JSON valide enregistré dans facture_analysee.json")
    except json.JSONDecodeError as e:
        print(" Erreur lors du parsing JSON :")
        print(e)
        print("\n--- Réponse brute du modèle (Gemma3) ---\n")
        print(output)