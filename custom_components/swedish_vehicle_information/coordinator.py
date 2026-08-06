import logging
from datetime import date, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api.carinfo import fetch_carinfo
from .const import CONF_REG_NUMBERS, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Coordinatorn kollar en gång om dagen VILKA fordon som är dags att hämta
# på nytt. Det faktiska hämtningsintervallet per fordon avgörs istället av
# _interval_for() nedan, baserat på hur nära besiktningen är.
CHECK_INTERVAL = timedelta(days=1)

INTERVAL_FAR = timedelta(days=14)    # mer än 3 veckor kvar till besiktning
INTERVAL_SOON = timedelta(days=7)    # 2–3 veckor kvar
INTERVAL_URGENT = timedelta(days=1)  # mindre än 2 veckor kvar (eller okänt datum)

DAYS_3_WEEKS = 21
DAYS_2_WEEKS = 14


class SwedishVehicleCoordinator(DataUpdateCoordinator):
    """Fetches car.info data with an adaptive per-plate interval.

    För att inte belasta car.info i onödan hämtas varje registreringsnummer
    bara när dess eget "nästa hämtning tidigast"-datum har passerat. Hur ofta
    det sker beror på hur nära nästa besiktning är:

      - mer än 3 veckor kvar  -> hämta igen om 14 dagar
      - 2-3 veckor kvar        -> hämta igen om 7 dagar
      - mindre än 2 veckor kvar -> hämta igen imorgon

    Vid varje omstart av Home Assistant hämtas alla fordon direkt (via
    async_config_entry_first_refresh, som HA alltid kör vid uppstart), så
    vi behöver inte spara tidsstämplar till disk mellan omstarter — klockan
    nollställs naturligt varje gång.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.plates = [
            plate.strip().upper().replace(" ", "")
            for plate in entry.data[CONF_REG_NUMBERS].split(",")
            if plate.strip()
        ]

        # Håller reda på när varje fordon tidigast får hämtas igen.
        # Tomt vid start -> alla fordon hämtas direkt vid första uppdateringen.
        self._next_due: dict[str, date] = {}

        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=CHECK_INTERVAL,
        )

    @staticmethod
    def _interval_for(next_inspection: str | None) -> timedelta:
        """Räkna ut hämtningsintervall baserat på dagar kvar till besiktning."""
        if not next_inspection:
            # Okänt datum (t.ex. tillfälligt fel vid hämtning) -> kolla igen
            # imorgon istället för att riskera att vänta 14 dagar i onödan.
            return INTERVAL_URGENT

        try:
            deadline = date.fromisoformat(next_inspection)
        except ValueError:
            return INTERVAL_URGENT

        days_left = (deadline - date.today()).days

        if days_left > DAYS_3_WEEKS:
            return INTERVAL_FAR
        if days_left > DAYS_2_WEEKS:
            return INTERVAL_SOON
        return INTERVAL_URGENT

    async def _async_update_data(self) -> dict:
        """Hämta bara de fordon vars tur det är, behåll övrig data oförändrad."""
        today = date.today()
        data = dict(self.data or {})

        for plate in self.plates:
            due = self._next_due.get(plate)

            if due is not None and today < due:
                _LOGGER.debug("Hoppar över %s, nästa hämtning: %s", plate, due)
                continue

            _LOGGER.debug("Hämtar car.info-data för %s", plate)
            vehicle_data = await fetch_carinfo(self.hass, plate)
            data[plate] = vehicle_data

            interval = self._interval_for(vehicle_data.get("nextInspection"))
            self._next_due[plate] = today + interval
            _LOGGER.debug(
                "%s: nästa hämtning tidigast %s (intervall %s)",
                plate,
                self._next_due[plate],
                interval,
            )

        return data
