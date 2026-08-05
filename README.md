![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)


# Swedish Vehicle Information – v1.0.0

Första officiella versionen av Home Assistant‑integrationen **Swedish Vehicle Information**.

## ✨ Funktioner

- Hämtar fordonsdata från:
  - **Transportstyrelsen** (HTML‑scraping via POST)
  - **Biluppgifter.se** (HTML‑scraping via GET)
- Ingen API‑nyckel krävs
- Provider‑fallback: TS → Biluppgifter
- Dynamisk uppdateringsfrekvens:
  - Vid omstart: direkt uppdatering
  - >14 dagar till nästa besiktning: 1 gång/vecka
  - ≤14 dagar: 1 gång/dag
- En sensor per fordon
- Rådata från båda providers för felsökning

## 🔧 Installation

1. Lägg till detta repo som ett **Custom Repository** i HACS.
2. Installera integrationen.
3. Starta om Home Assistant.
4. Lägg till integrationen via:
   *Inställningar → Enheter & tjänster → Lägg till integration → Swedish Vehicle Information*
5. Ange ett eller flera registreringsnummer (kommaseparerade).

## 📦 Innehåll

- Transportstyrelsen‑scraper (`api/transportstyrelsen.py`)
- Biluppgifter‑scraper (`api/biluppgifter.py`)
- Provider‑fallback och dynamisk intervall (`coordinator.py`)
- Sensor per fordon (`sensor.py`)
- Full dokumentation i README.md

## 🛠 Felsökning

- Kontrollera att registreringsnumret är korrekt.
- Vissa fordon saknar publika ägaruppgifter.
- Rå HTML finns i sensorns attribut för felsökning.

## ❤️ Tack

Tack för att du använder Swedish Vehicle Information.  
Förslag, förbättringar och pull requests är varmt välkomna!




# Swedish Vehicle Information

Home Assistant‑integration som hämtar fordonsdata från:

- **Transportstyrelsen**  
  via HTML‑scraping av den officiella fordonsuppgiftssidan  
  (ingen API‑nyckel krävs)

- **Biluppgifter.se**  
  via HTML‑scraping av fordonsvyn  
  (ingen API‑nyckel krävs)

Integrationen använder **provider‑fallback**:

1. Transportstyrelsen (TS)  
2. Biluppgifter.se (BU)

Om en källa saknar data eller misslyckas används nästa källa automatiskt.

---

## Funktioner

Varje fordon blir en egen sensor med:

- Fordonsstatus  
- Senaste besiktning  
- Nästa besiktning  
- Fordonsskatt  
- Ägare (om publikt)  
- Fordonstyp  
- Rådata från båda providers  
- Dynamisk uppdateringsfrekvens baserad på nästa besiktning

---

## Uppdateringsfrekvens

Integrationen justerar automatiskt hur ofta data hämtas:

- **Vid omstart:** alltid direkt uppdatering  
- **Mer än 14 dagar till nästa besiktning:** uppdatering 1 gång/vecka  
- **14 dagar eller mindre:** uppdatering 1 gång/dag  

Detta minskar belastning och onödiga anrop.

---

## Datakällor

### Transportstyrelsen (TS)

Data hämtas via en POST‑förfrågan mot:

https://fordon-fu-regnr.transportstyrelsen.se/UppgifterAnnatFordon/Fordonsuppgifter

Kod

Integrationen skickar:

- `Registreringsnummer`
- `recaptchaClientToken` (tomt)
- `Captcha_CaptchaResponse` (tomt)

Transportstyrelsen returnerar en HTML‑sida som parsas för relevanta värden.

### Biluppgifter.se (BU)

Data hämtas via en GET‑förfrågan mot:

https://biluppgifter.se/fordon/<REGNR>/

Kod

Sidan innehåller tabeller med fordonsdata som parsas automatiskt.

---

## Attribut i sensorn

| Attribut | Källa | Beskrivning |
|----------|--------|-------------|
| `status` | TS/BU | Fordonsstatus |
| `last_inspection` | TS/BU | Senaste besiktning |
| `next_inspection` | TS/BU | Nästa besiktning |
| `tax` | TS/BU | Fordonsskatt |
| `owner` | BU | Ägare (om publikt) |
| `vehicle_type` | BU | Fordonstyp |
| `transportstyrelsen` | TS | Rådata från TS |
| `biluppgifter` | BU | Rådata från BU |

---

## Felsökning

### Ingen data visas?
- Kontrollera att registreringsnumret är korrekt.
- Vissa fordon saknar publika ägaruppgifter.
- Biluppgifter.se kan blockera extremt frekventa anrop — dynamisk intervall minimerar detta.

### Vill du se rå HTML?
Rådata från båda providers finns i sensorns attribut under:

- `transportstyrelsen.raw_html`
- `biluppgifter.raw_html`

---

## Licens

Fri att använda och modifiera.

---