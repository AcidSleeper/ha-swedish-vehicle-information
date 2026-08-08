# Changelog

Alla nämnvärda ändringar i det här projektet dokumenteras i den här filen.

## [0.1.0] - 2026-08-xx

Beta-testet har gått bra. Lyfter nu upp versionsnumret till v0.1.0 för att
visa en stabil version.

---

## [0.0.5-beta-4] - 2026-08-08

Nuvarande beta-version under testning.

### Added
- Ny datakälla **biluppgifter.se** som komplement till Car.info
- Schemalagd, veckodagsbaserad hämtning: Car.info hämtas tisdagar kl 10:00,
  biluppgifter.se fredagar kl 10:00, med frekvens (var 14:e dag / varje
  vecka / båda dagarna) beroende på hur nära besiktningen är
- Automatisk **fallback** mellan källorna om den ordinarie källan för ett
  hämtningstillfälle misslyckas (fungerar åt båda hållen)
- Nytt attribut `kalla` — visar vilken källa (`car.info` eller
  `biluppgifter.se`) den senaste datan faktiskt hämtades från
- Alla fordon hämtas alltid direkt vid uppstart av Home Assistant

### Changed
- Statusvärdet (`i_trafik`) normaliseras nu till `Ja`/`Nej` oavsett vilken
  källa som svarade — biluppgifter.se skriver annars ut beskrivande text
  som `"I Trafik"`
- `fabrikat` normaliseras till Versal + gemener (t.ex. `Björnsläpet`
  istället för `BjÖrnslÄpet`, som var vad Car.info faktiskt levererade)

### Fixed
- Åtgärdat en bugg där Home Assistant-uppstart på en fredag felaktigt
  gjorde biluppgifter.se till primärkälla istället för Car.info

---

## [0.4.0] - 2026-08-07

### Added
- Nytt attribut `korforbud` (`Ja`/`Nej`) baserat på om `besiktas_senast`
  har passerat dagens datum
- Nytt attribut `fabrikat` — fordonets märke/modell, parsat från källans
  sida (fungerar för bil, släp och motorcykel)
- Exempel-dashboard (valfritt, installeras inte av HACS):
  `custom_templates/fordon_status.jinja` (Jinja-macron) och
  `UI-suggestions/besiktning.yaml` (färdigt Mushroom-kort)

### Changed
- Attributet `raw_html` (fullständig sidkälla, användes bara vid
  felsökning) har tagits bort ur sensorn
- Nytt attribut `i_trafik` tillagt som eget attribut, separat från
  sensorns state

### Fixed
- Bytt bort opålitlig parsning av "I trafik" via meta-description (var tom
  för vissa fordonstyper, t.ex. släp) mot en mer robust metod baserad på
  sidans generella specifikationsstruktur — verifierat mot bil, släp och
  motorcykel

---

## [0.0.3] - 2026-08-07

### Added
- **Adaptivt uppdateringsintervall** infört: fordon med mer än 3 veckor
  kvar till besiktning hämtas var 14:e dag, 2–3 veckor kvar hämtas var
  7:e dag, mindre än 2 veckor kvar hämtas dagligen

### Fixed
- Bytt bort gissade JSON-LD-fält för besiktningsdatum mot faktisk parsning
  av sidans verkliga HTML-struktur, efter verifiering mot riktig
  sidkälla — de tidigare fältnamnen (`dateOfLastInspection` /
  `dateOfNextInspection`) existerade inte på Car.info

---

## [0.0.2] - 2026-08-06

Första fungerande versionen efter felsökning av den ursprungliga koden.

### Added
- Stöd för flera registreringsnummer (komma‑separerade)
- Attribut `besiktad` och `besiktas_senast`
- Diagnostik-stöd (`diagnostics.py`) med korrekt attributnamn
- Översättningar (`sv.json` / `en.json`) med korrekt fältnyckel och
  felmeddelanden för konfigurationsformuläret

### Fixed
- `KeyError` vid uppstart orsakat av att `config_flow.py` och
  `coordinator.py`/`sensor.py` använde olika nycklar (`reg_numbers` vs
  `plate`)
- Saknat beroende `beautifulsoup4` i `manifest.json`
  (gav `ModuleNotFoundError`)
- Felaktig logger-konfiguration i coordinatorn
  (`AttributeError: 'HomeAssistant' object has no attribute 'logger'`)
- `update_interval=None` som gjorde att integrationen aldrig uppdaterade
  sig själv automatiskt
- Felet *"No setup or config entry setup function defined"* orsakat av
  felaktig `__init__.py`
- Felaktig URL till Car.info som saknade landskoden `S/`
  (rätt format: `.../license-plate/S/ABC123`), vilket gav tom/felaktig data
- `AttributeError` i `diagnostics.py` (`coordinator.vehicles` fanns inte,
  rätt attribut heter `coordinator.plates`)
- Felaktig datanyckel i `en.json`/`sv.json` som gjorde att
  konfigurationsformuläret visade rå textnyckel istället för översatt text
