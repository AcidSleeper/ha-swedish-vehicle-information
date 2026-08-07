import logging
from datetime import date, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .api.biluppgifterse import fetch_biluppgifter
from .api.carinfo import fetch_carinfo
from .const import CONF_REG_NUMBERS, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Coordinatorn kollar en gång i timmen om det är dags för ett av de två fasta
# hämtningsfönstren nedan. Det är en billig operation (bara datum/tid-
# jämförelser) - riktiga nätverksanrop görs bara när ett fönster faktiskt
# är öppet OCH fordonets egen tur har kommit (se _tier_for).
CHECK_INTERVAL = timedelta(hours=1)

# Transportstyrelsen uppdaterar car.info natten mot tisdag, och
# biluppgifter.se någon gång under veckan (oftast fredagar enligt egen
# uppgift). Vi hämtar därför tidigast kl 10:00 på respektive dag för att
# ge källorna tid att hinna uppdateras.
CARINFO_WEEKDAY = 1       # tisdag (Python: måndag=0 ... söndag=6)
BILUPPGIFTER_WEEKDAY = 4  # fredag
FETCH_HOUR = 10

# Hämtningsintervall + vilka veckodagar som är "tillåtna" för respektive nivå.
# FAR/SOON använder bara car.info (tisdagar). URGENT (nära besiktning/
# körförbud) använder båda fönstren för att komma så nära "varje dag" som
# meningsfullt är, givet att källorna ändå bara uppdateras en gång i veckan.
INTERVAL_FAR = timedelta(days=14)
INTERVAL_SOON = timedelta(days=7)
INTERVAL_URGENT = timedelta(days=1)

DAYS_3_WEEKS = 21
DAYS_2_WEEKS = 14


class SwedishVehicleCoordinator(DataUpdateCoordinator):
    """Fetches vehicle data from car.info (tisdagar) och biluppgifter.se
    (fredagar), med adaptivt intervall per fordon och automatisk fallback
    mellan källorna vid fel.

    Regler:
      - mer än 3 veckor kvar till besiktning -> hämta var 14:e dag, alltid
        på en tisdag, via car.info
      - 2-3 veckor kvar -> hämta varje tisdag via car.info
      - mindre än 2 veckor kvar -> hämta på både tisdagar (car.info) och
        fredagar (biluppgifter.se)
      - misslyckas hämtningen från den ordinarie källan för fönstret,
        provas den andra källan automatiskt som fallback
      - vid uppstart av Home Assistant hämtas alla fordon direkt, oavsett
        veckodag, med car.info som primär källa
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.plates = [
            plate.strip().upper().replace(" ", "")
            for plate in entry.data[CONF_REG_NUMBERS].split(",")
            if plate.strip()
        ]

        self._last_fetch_date: dict[str, date] = {}
        self._next_due: dict[str, date] = {}

        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=CHECK_INTERVAL,
        )

    @staticmethod
    def _tier_for(next_inspection: str | None, today: date) -> tuple[timedelta, set[int]]:
        """Returnera (intervall, tillåtna veckodagar) baserat på dagar kvar."""
        if not next_inspection:
            # Okänt datum -> behandla som akut tills vi fått ett giltigt värde.
            return INTERVAL_URGENT, {CARINFO_WEEKDAY, BILUPPGIFTER_WEEKDAY}

        try:
            deadline = date.fromisoformat(next_inspection)
        except ValueError:
            return INTERVAL_URGENT, {CARINFO_WEEKDAY, BILUPPGIFTER_WEEKDAY}

        days_left = (deadline - today).days

        if days_left > DAYS_3_WEEKS:
            return INTERVAL_FAR, {CARINFO_WEEKDAY}
        if days_left > DAYS_2_WEEKS:
            return INTERVAL_SOON, {CARINFO_WEEKDAY}
        return INTERVAL_URGENT, {CARINFO_WEEKDAY, BILUPPGIFTER_WEEKDAY}

    @staticmethod
    def _next_allowed_weekday(from_date: date, weekdays: set[int]) -> date:
        """Första datum >= from_date vars veckodag finns i `weekdays`."""
        d = from_date
        while d.weekday() not in weekdays:
            d += timedelta(days=1)
        return d

    async def _fetch_with_fallback(
        self, plate: str, today: date, prefer_carinfo: bool = False
    ) -> dict | None:
        """Hämta ett fordon via rätt källa för dagens fönster, med fallback
        till den andra källan om den ordinarie misslyckas.

        `prefer_carinfo=True` tvingar car.info som förstaval oavsett
        veckodag - används vid den allra första hämtningen (Home Assistant-
        uppstart), där vi ännu inte vet fordonets nivå/tier och därför
        default:ar till car.info som primärkälla enligt ursprungskravet.
        """
        use_biluppgifter_first = (
            today.weekday() == BILUPPGIFTER_WEEKDAY and not prefer_carinfo
        )

        if use_biluppgifter_first:
            primary = (fetch_biluppgifter, "biluppgifter.se")
            fallback = (fetch_carinfo, "car.info")
        else:
            primary = (fetch_carinfo, "car.info")
            fallback = (fetch_biluppgifter, "biluppgifter.se")

        (primary_fn, primary_name) = primary
        (fallback_fn, fallback_name) = fallback

        try:
            _LOGGER.debug("Hämtar %s från %s", plate, primary_name)
            result = await primary_fn(self.hass, plate)
            result["source"] = primary_name
            return result
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Misslyckades hämta %s från %s (%s) - provar %s istället",
                plate,
                primary_name,
                err,
                fallback_name,
            )

        try:
            result = await fallback_fn(self.hass, plate)
            result["source"] = fallback_name
            return result
        except Exception as err:  # noqa: BLE001
            _LOGGER.error(
                "Misslyckades hämta %s även från %s (%s)", plate, fallback_name, err
            )
            return None

    async def _async_update_data(self) -> dict:
        now = dt_util.now()
        today = now.date()
        data = dict(self.data or {})

        for plate in self.plates:
            is_first_fetch = plate not in self._last_fetch_date

            if not is_first_fetch:
                already_done_today = self._last_fetch_date.get(plate) == today
                due = self._next_due.get(plate)

                if already_done_today:
                    continue
                if due is None or today < due:
                    continue
                # today == due -> vänta in kl 10:00. today > due -> vi har
                # missat fönstret (t.ex. HA var avstängd) och kör direkt
                # (catch-up) istället för att vänta en hel vecka till.
                if today == due and now.hour < FETCH_HOUR:
                    continue

            _LOGGER.debug(
                "%s: %s",
                plate,
                "första hämtningen vid uppstart" if is_first_fetch else "hämtningsfönster öppet",
            )

            vehicle_data = await self._fetch_with_fallback(
                plate, today, prefer_carinfo=is_first_fetch
            )

            if vehicle_data is None:
                # Båda källorna misslyckades - behåll gammal data, försök
                # igen vid nästa timkontroll istället för att vänta en vecka.
                continue

            data[plate] = vehicle_data
            self._last_fetch_date[plate] = today

            interval, weekdays = self._tier_for(vehicle_data.get("nextInspection"), today)
            self._next_due[plate] = self._next_allowed_weekday(today + interval, weekdays)
            _LOGGER.debug(
                "%s: nästa hämtning tidigast %s", plate, self._next_due[plate]
            )

        return data
