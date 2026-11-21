# Changelog

Alla nämnvärda ändringar i det här projektet dokumenteras i den här filen.

---

## [0.1.3] - 2026-11-21

### Added
 - En fil: hacs.json
 - Krävs numera genom Marknadsplatsen i Home Assistant

---

## [0.1.1] - 2026-11-21

### Fixed
- car.info ändrade sin HTML-markup för besiktningsdatum i november 2026.
  `_parse_inspection_dates()` läser nu `featured_info_group`/`group_item`
  (etikett i `div.text-end.text-truncate`, värde i
  `div.fw-bold.text-truncate.text-end`). Den äldre `featured_info_item`-parsern
  finns kvar som fallback. Detta återställer `besiktad`, `besiktas_senast` och
  det härledda `korforbud` för samtliga fordon.

### Added
- Validering av hämtningsresultat: ett tomt eller blankt `nextInspection`
  räknas som en misslyckad hämtning och utlöser automatisk fallback till den
  andra källan (car.info ↔ biluppgifter.se).
- Persistent avisering i Home Assistants Aviseringar-meny när fallback sker.
  Titel: `Swedish Vehicle Information`. Stabilt `notification_id` per
  registreringsnummer gör att upprepade fel uppdaterar samma avisering i
  stället för att skapa nya. Om även fallbacken misslyckas uppdateras samma
  avisering med slutfelet och texten "Ingen data uppdaterad". Aviseringen
  rensas inte automatiskt.
- `persistent_notification` tillagt som beroende i `manifest.json`.

### Changed
- `_fetch_with_fallback()` i `coordinator.py` loggar nu orsaken till ett fel
  (undantag eller tomt besiktningsdatum) och tar med den i aviseringen.
- Manifestets `dependencies` ändrades från `[]` till
  `["persistent_notification"]`. Manifestversionen är oförändrad
  (`v0.0.5-beta-6`).

### Berörda filer
- `custom_components/swedish_vehicle_information/api/carinfo.py`
- `custom_components/swedish_vehicle_information/coordinator.py`
- `custom_components/swedish_vehicle_information/manifest.json`

---

## [0.1.0] - 2026-08-27

Första stabila release, efter godkänt betatest genom `v0.0.5-beta-1`
till `v0.0.5-beta-6`.

### Changed
- Exempel-dashboarden använder inte längre **card-mod** för styling —
  bytt till [**UIX (UI eXtension)**](https://github.com/Lint-Free-Technology/uix),
  card-mods efterföljare (se README för installationskrav)

*(Övriga ändringar från beta-perioden listas under respektive
beta-version nedan — inga ytterligare funktionsändringar utöver
ovanstående gjordes inför den stabila releasen.)*

---

## [0.0.5-beta-6] - 2026-08-18

Nuvarande betabygge, under testning på developer-instans.

### Changed
- Uppdateringsfrekvensen för fordon nära besiktning (mindre än 2 veckor
  kvar, eller redan körförbud) har höjts från "tisdagar + fredagar"
  (~var 3–4:e dag) till **varje dag**. Car.info används de flesta dagarna,
  biluppgifter.se på fredagar, med fallback mellan källorna tillgänglig
  alla dagar.

### Fixed
- Fördröjd datauppdatering efter en genomförd besiktning — bekräftat i
  ett fall där både Car.info och biluppgifter.se redan hade rätt,
  uppdaterat besiktningsdatum, men integrationen inte hämtade det
  förrän nästa schemalagda tisdag/fredag-fönster. Grundorsaken var ett
  för optimistiskt antagande om att källorna bara uppdateras exakt en
  gång i veckan på en förutsägbar dag — det stämmer inte alltid.

---

## [0.0.5-beta-5] - 2026-08-08

Nuvarande betabygge, under testning på developer-instans.

### Changed
- `fabrikat` hämtas nu alltid från biluppgifter.se:s dedikerade
  `Fabrikat`-fält istället för att härledas från Car.infos `<title>`-tagg.
  Värdet cachas per registreringsnummer så det bara hämtas en gång (inte
  vid varje schemalagd uppdatering), eftersom fabrikat aldrig ändras för
  ett givet fordon.

### Fixed
- Felaktigt fabrikat för vissa fordon (bekräftat på en Derbi-moped som
  Car.info internt felklassificerat under bilmärket "DS") — löst genom att
  byta primärkälla för just fabrikat-fältet till biluppgifter.se, som har
  ett dedikerat märkesfält istället för Car.infos fritext-baserade titel

---

## [0.0.5-beta-4] - 2026-08-08

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
