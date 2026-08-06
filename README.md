![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)
![Version](https://img.shields.io/badge/version-0.0.3-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)


# Swedish Vehicle Information (Car.info Integration)

Ett Home Assistant‑tillägg som hämtar fordonsinformation från **Car.info** baserat på svenska registreringsnummer.  
Integrationens fokus är att leverera fyra centrala värden:

- **I trafik** – Fordonets trafikstatus  
- **Besiktad** – Datum för senaste besiktning  
- **Besiktas senast** – Sista datum för nästa besiktning
- **Körförbud** - Har sista datum för besiktning passerats

Detta gör integrationen enkel, snabb och stabil utan beroenden till Transportstyrelsen som har ett invecklat system.

---

## ✨ Funktioner

- Hämtar fordonsdata från Car.info
- Stöd för flera registreringsnummer (komma‑separerade)
- Visar status som sensor‑state
- Visar besiktningsdata som attribut
- Uppdaterar automatiskt en gång per dag
- Fullt stöd för Home Assistant config‑flow

---

## 📦 Installation

Det rekommenderade sättet att installera integrationen är via **HACS**.

### 1. Lägg till som Custom Repository
1. Öppna **HACS** i Home Assistant  
2. Gå till **Integrations**  
3. Klicka på **⋮ (meny) → Custom repositories**  
4. Lägg till ditt GitHub‑repo: https://github.com/AcidSleeper/ha-swedish-vehicle-information/ 
5. Välj kategori: **Integration**

### 2. Installera integrationen
1. Sök efter **Swedish Vehicle Information** i HACS  
2. Installera  
3. Starta om Home Assistant

---

## ⚙️ Konfiguration

1. Gå till **Inställningar → Enheter & tjänster**
2. Klicka på **Lägg till integration**
3. Sök efter **Swedish Vehicle Information**
4. Ange ett eller flera registreringsnummer, t.ex.:

ABC123, ACB132

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
- `besiktad` – senaste besiktning  
- `besiktas_senast` – nästa besiktning  
- `registreringsnummer` - ABC123
- `korforbud` - ja eller nej

###Exempel på kort
https://github.com/AcidSleeper/ha-swedish-vehicle-information/blob/main/UI-Suggestions/Sk%C3%A4rmbild%202026-08-06%20235110.png

---

## 🔄 Uppdateringsintervall

Integrationens coordinator uppdaterar data **en gång per dag**.  

---

## 🧩 Datakälla

All data hämtas från:

https://www.car.info/sv-se/license-plate/S/<REGNUMMER>

---

## 🛠 Support

Detta tillägg är skapat för privat bruk och är inte officiellt kopplat till Car.info. 
Fordon som testats är personbil, motorcykel, släpvagn och moped.
För frågor, förbättringar eller buggar — öppna ett ärende i GitHub‑repot.
