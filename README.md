# Swedish Vehicle Information

Home Assistant-integration som hämtar fordonsdata från:
- Transportstyrelsen (HTML-scraping, ingen API-nyckel)
- Fordonsuppgifter (API)
- Biluppgifter (API)

Varje fordon blir en egen sensor med flera attribut:
- status
- senaste besiktning
- nästa besiktning
- skatt
- ägare
- fordonsklass
- rådata per provider

## Installation

1. Kopiera `custom_components/swedish_vehicle_information` till din Home Assistant-konfiguration.

2. Starta om Home Assistant.

3. Lägg till integrationen via:
   Inställningar → Enheter & tjänster → Lägg till integration → Swedish Vehicle Information.

4. Ange registreringsnummer (kommaseparerade).

## Uppdateringsfrekvens

- Vid omstart: alltid uppdatering direkt.
- Mer än 14 dagar till nästa besiktning: uppdatering 1 gång/vecka.
- Mindre än 14 dagar: uppdatering 1 gång/dag.

## Providers

Transportstyrelsen:
- HTML-sida: https://fordon-fu-regnr.transportstyrelsen.se/UppgifterAnnatFordon/Fordonsuppgifter
- Scraping-logik finns i `api/transportstyrelsen.py`.
- Justera selectors efter verklig HTML-struktur.

Fordonsuppgifter / Biluppgifter:
- Justera `api/fordonsuppgifter.py` och `api/biluppgifter.py` med korrekta endpoints och API-nycklar.
