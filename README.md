# SolsticeHub

> A Home Assistant integration for sun-based calendar systems: precise
> astronomical seasons, the Celtic Wheel of the Year, and the Chinese solar
> terms — with exact timestamps, countdowns and daylight-trend tracking.

[![GitHub Release](https://img.shields.io/github/v/release/moerk-o/ha-solsticehub?style=flat-square)](https://github.com/moerk-o/ha-solsticehub/releases)
[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41bdf5?style=flat-square&logo=homeassistant)](https://www.home-assistant.io/)

> **Upgrading from "Solstice Season" (v1.x)?** SolsticeHub is the renamed
> successor. The domain changed, so a manual migration is required — see
> [Migrating from Solstice Season](#migrating-from-solstice-season).

## What it does

Home Assistant's built-in [Season integration](https://www.home-assistant.io/integrations/season/)
provides only the current astronomical/meteorological season. SolsticeHub adds
detail and more calendar systems, all calculated locally with
[PyEphem](https://rhodesmill.org/pyephem/) — no internet connection required.

When you add the integration you pick a **device type**. Each instance creates
one device with its own sensors; you can add several (e.g. one Four Seasons and
one Chinese Solar Terms device).

| Device type | What you get |
|-------------|--------------|
| **Four Seasons** | Current season + timestamps for each equinox/solstice + next season change |
| **Cross-Quarter / Celtic** | The Wheel of the Year (Imbolc, Ostara, Beltane, Litha, Lughnasadh, Mabon, Samhain, Yule) |
| **Chinese Solar Terms** | The 24 solar terms (or the 8 major ones) |

Every device additionally exposes the **shared sun-data sensors**: a daylight
trend (are the days getting longer or shorter?), the timestamp of the next
trend change (the next solstice), and a diagnostic solar-longitude sensor
(disabled by default).

## Installation

### HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=moerk-o&repository=ha-solsticehub)

1. Click the button above, or search for **SolsticeHub** in HACS
2. Install the integration and restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for **SolsticeHub** and follow the setup wizard

### Manual

1. Download the latest release from [GitHub Releases](https://github.com/moerk-o/ha-solsticehub/releases)
2. Copy `custom_components/solsticehub` into your `config/custom_components/` directory
3. Restart Home Assistant and add the integration via the UI

## Configuration

Configuration is done entirely through the UI. Step 1 asks for a name and the
device type; step 2 collects type-specific options.

| Device type | Options |
|-------------|---------|
| Four Seasons | Hemisphere (auto-filled from your Home location), Mode (astronomical / meteorological) |
| Cross-Quarter | Mode (astronomical midpoints / traditional fixed dates), Naming (system language / Celtic) |
| Chinese Solar Terms | Scope (all 24 / 8 major), Naming (system language / Pinyin / Hanzi) |

### Calculation modes (Four Seasons)

- **Astronomical** – seasons begin at the exact equinoxes and solstices (dates
  shift slightly each year). Calculated with PyEphem.
- **Meteorological** – seasons begin on fixed calendar dates (Mar/Jun/Sep/Dec
  1st, offset by six months in the southern hemisphere).

Hemisphere mapping is handled automatically. For the full reasoning and the
hemisphere/daylight-trend details, see [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md).

## Entities

### Shared sun-data sensors (every device)

| Entity | Type | Description |
|--------|------|-------------|
| `daylight_trend` | enum | `days_getting_longer` / `days_getting_shorter` / `solstice_today` |
| `next_daylight_trend_change` | timestamp | The next solstice (turning point of the trend) |
| `solar_longitude` | measurement (°) | Ecliptic longitude of the Sun (diagnostic, disabled by default) |

### Four Seasons

| Entity | Type | Notable attributes |
|--------|------|--------------------|
| `current_season` | enum (`spring`/`summer`/`autumn`/`winter`) | `mode`, `hemisphere`, `season_age`, `season_progress` |
| `spring_equinox`, `summer_solstice`, `autumn_equinox`, `winter_solstice` | timestamp | `days_until`, `last_start` |
| `next_season_change` | timestamp | `days_until`, `event_type` |

### Cross-Quarter / Celtic

| Entity | Type | Notable attributes |
|--------|------|--------------------|
| `current_period` | enum (the eight festivals) | `mode`, `period_age`, `events` |
| `next_period_change` | timestamp | `days_until`, `event_type` |

### Chinese Solar Terms

| Entity | Type | Notable attributes |
|--------|------|--------------------|
| `current_term` | enum (24 or 8 terms) | `scope`, `term_age`, `events` |
| `next_term_change` | timestamp | `days_until`, `event_type` |

All timestamps are stored in UTC; Home Assistant displays them in your local
timezone.

## Migrating from Solstice Season

SolsticeHub is the renamed successor of the *Solstice Season* integration. The
Home Assistant domain changed from `solstice_season` to `solsticehub`, and Home
Assistant cannot migrate configuration across domains. To upgrade:

1. Remove the old **Solstice Season** integration (Settings → Devices &
   Services). You may also remove the old HACS repository.
2. Install **SolsticeHub** (see [Installation](#installation)).
3. Add the device type(s) you want and repoint any automations/dashboards to
   the new entities.

The previous v1.x behaviour corresponds to the **Four Seasons** device type;
the daylight-trend sensors that used to be separate are now included with it.

## Localization

Sensor names and states are translated via Home Assistant's translation system.
Currently supported: English (fallback), German, Dutch.

## Documentation

- Technical reference: [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)
- Release history: [RELEASENOTES.md](RELEASENOTES.md) (v1.x: [RELEASENOTES_v1.md](RELEASENOTES_v1.md))

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

- Inspired by the [Home Assistant Season integration](https://www.home-assistant.io/integrations/season/)
- Astronomical calculations powered by [PyEphem](https://rhodesmill.org/pyephem/)
