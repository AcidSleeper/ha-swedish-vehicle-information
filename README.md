![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)
![Version](https://img.shields.io/badge/version-0.0.4-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)


# Swedish Vehicle Information (Car.info Integration)

Ett Home Assistant‑tillägg som hämtar fordonsinformation från **Car.info** baserat på svenska registreringsnummer.  
Integrationens fokus är att leverera fem centrala värden:

- **I trafik** – Fordonets trafikstatus  
- **Besiktad** – Datum för senaste besiktning  
- **Besiktas senast** – Sista datum för nästa besiktning
- **Fabrikat** - Fordonets märke/modell, t.ex. Subaru eller Kia
- **Körförbud** - Har sista datum för besiktning passerats

Detta gör integrationen enkel och snabb.

---

## ✨ Funktioner

- Hämtar fordonsdata från Car.info
- Stöd för flera registreringsnummer (komma‑separerade)
- Visar status som sensor‑state
- Visar besiktningsdata som attribut
- Adaptivt uppdateringsintervall — hämtar oftare ju närmare besiktningen är (se nedan)
- Fullt stöd för Home Assistant config‑flow

---

## 📦 Installation

Det rekommenderade sättet att installera integrationen är via **HACS**.

### 1. Lägg till som Custom Repository
1. Öppna **HACS** i Home Assistant  
2. Gå till **Integrations**  
3. Klicka på **⋮ (meny) → Custom repositories**  
4. Lägg till GitHub‑repo: https://github.com/AcidSleeper/ha-swedish-vehicle-information/ 
5. Välj kategori: **Integration**

### 2. Installera integrationen
1. Sök efter **Swedish Vehicle Information** i HACS  
2. Installera  
3. Starta om HACS / Home Assistant

---

## ⚙️ Konfiguration

1. Gå till **Inställningar → Enheter & tjänster**
2. Klicka på **Lägg till integration**
3. Sök efter **Swedish Vehicle Information**
4. Ange ett eller flera registreringsnummer, t.ex.:

ABC123, ACB132, ABC321

Klart!

---

## 📊 Sensorer

För varje registreringsnummer skapas en sensor:

### **State**
- `I trafik`
- `Avställd`
- `Avregistrerad`
- etc.

### **Attribut**
- `fabrikat` – fordonets märke/modell, t.ex. Subaru / Volvo
- `besiktad` – senaste besiktning  
- `besiktas_senast` – nästa besiktning  
- `registreringsnummer` - ABC123
- `korforbud` - ja eller nej

---

## 🔄 Uppdateringsintervall

Integrationen använder ett **adaptivt** uppdateringsintervall per registreringsnummer,
istället för ett fast intervall för alla fordon. Det håller nere antalet anrop till
Car.info, särskilt om du har flera fordon.

Hur ofta ett fordon hämtas på nytt beror på hur nära nästa besiktning är:

| Dagar kvar till besiktning | Hämtas på nytt |
|---|---|
| Mer än 3 veckor | Var 14:e dag |
| 2–3 veckor | Var 7:e dag |
| Mindre än 2 veckor | Varje dag |

Alla registreringsnummer hämtas alltid direkt vid uppstart av Home Assistant,
oavsett var i intervallet de befinner sig.

---

## 🧩 Datakälla

All data hämtas från:

https://www.car.info/sv-se/license-plate/S/<REGNUMMER>

---

## 🖥️ Dashboard-exempel (valfritt)

Repot innehåller ett exempel på en färdig dashboard-vy för besiktningsinformation,
byggd med [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) och
[card-mod](https://github.com/thomasloven/lovelace-card-mod). Det här är **valfritt**
och installeras inte automatiskt av HACS — filerna behöver kopieras manuellt till din
Home Assistant-konfiguration.

![](UI-Suggestions/example.png)

### Förutsättningar

Innan du använder exempel-dashboarden behöver följande vara installerat via HACS:

- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) (`custom:mushroom-template-card`)
- [card-mod](https://github.com/thomasloven/lovelace-card-mod)

### 1. Jinja-mallar (`custom_templates/fordon_status.jinja`)

Filen innehåller Jinja-macron som räknar ut dagar kvar till besiktning, väljer
ikonfärg baserat på körförbud, och formaterar sekundärtexten i korten.

**Installation:**

1. Kopiera `custom_templates/fordon_status.jinja` från repot till
   `config/custom_templates/fordon_status.jinja` i din Home Assistant-installation
   (skapa mappen `custom_templates` om den inte redan finns).
2. Starta om Home Assistant.

Macro importeras i dashboard-korten med:

```jinja2
{% from 'fordon_status.jinja' import secondary %}
{{ secondary('sensor.vehicle_xxx000') }}
```

### 2. Färdigt dashboard-kort (`UI-suggestions/besiktning.yaml`)

Mappen `UI-suggestions/` innehåller ett komplett `vertical-stack`-kort
(`besiktning.yaml`) som visar en ruta per fordon med fabrikat, ikon,
dagar kvar till besiktning och röd markering vid körförbud.

**Installation:**

1. Kopiera innehållet i `UI-suggestions/besiktning.yaml`.
2. I din dashboard: lägg till ett nytt kort → växla till YAML-läge → klistra in.
3. Byt ut `entity`-värdena (t.ex. `sensor.vehicle_xxx000`) mot dina egna
   registreringsnummer-sensorer.

> **Obs:** Kortet förutsätter att `fordon_status.jinja` (steg 1 ovan) redan är
> installerad — annars visas ett template-fel i loggen.

---

## 🛠 Support

Detta tillägg är skapat för privat bruk och är inte officiellt kopplat till Car.info. 
Fordon som testats är personbil, motorcykel, släpvagn och moped.
För frågor, förbättringar eller buggar — öppna ett ärende i GitHub‑repot.
