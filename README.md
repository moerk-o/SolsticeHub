# Solstice Season

[![GitHub Release](https://img.shields.io/github/v/release/moerk-o/ha-solstice_season?style=flat-square)](https://github.com/moerk-o/ha-solstice_season/releases)
[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41bdf5?style=flat-square&logo=homeassistant)](https://www.home-assistant.io/)

A Home Assistant custom integration that provides precise astronomical season information with exact timestamps for solstices and equinoxes.

## Why This Integration?

Home Assistant's built-in [Season integration](https://www.home-assistant.io/integrations/season/) provides basic season information, but lacks detail. **Solstice Season** fills the gap by offering:

- **Precise timestamps** for all astronomical events (not just the current season)
- **Daylight trend tracking** - know whether days are getting longer or shorter
- **Countdown attributes** - `days_until` for each upcoming event
- **Both calculation modes** - astronomical (actual events) or meteorological (fixed dates)
- **Hemisphere support** - correct season mapping for both Northern and Southern hemispheres
- **Multi-instance capable** - track seasons for different locations

All calculations run locally using the [PyEphem](https://rhodesmill.org/pyephem/) library - no internet connection required.

## Understanding Seasons

### Calculation Modes

The integration offers two ways to determine seasons:

**Astronomical Mode** uses the actual position of the Earth relative to the Sun. Seasons begin at the exact moment of equinoxes and solstices - these dates shift slightly each year (typically between the 19th and 23rd of the month). This is how astronomers and most of the world define seasons.

**Meteorological Mode** uses fixed calendar dates based on the annual temperature cycle. Seasons always start on the 1st of the month (March, June, September, December). This is commonly used by meteorologists and statisticians because it aligns with calendar months, making climate data easier to compare.

### Hemispheres

The Earth's tilt means seasons are reversed between hemispheres:

| Event | Northern Hemisphere | Southern Hemisphere |
|-------|---------------------|---------------------|
| March Equinox | Spring begins | Autumn begins |
| June Solstice | Summer begins | Winter begins |
| September Equinox | Autumn begins | Spring begins |
| December Solstice | Winter begins | Summer begins |

The integration handles this automatically based on the configured hemisphere setting.

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=moerk-o&repository=ha-solstice_season)

1. Click the button above, or search for **Solstice Season** in HACS
2. Install the integration
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for **Solstice Season** and follow the setup wizard

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/moerk-o/ha-solstice_season/releases)
2. Copy the `custom_components/solstice_season` folder to your `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for **Solstice Season** and follow the setup wizard

## Configuration

The integration is configured entirely through the UI. No YAML required.

| Option | Description | Default |
|--------|-------------|---------|
| **Name** | Instance name (used as entity prefix) | `Home` |
| **Hemisphere** | Northern or Southern | Auto (based on configured Home location) |
| **Mode** | Astronomical or Meteorological | Astronomical |

### Calculation Modes

| Mode | Description |
|------|-------------|
| **Astronomical** | Based on actual equinoxes and solstices. Uses PyEphem for precise calculations. Dates vary slightly each year. |
| **Meteorological** | Based on fixed calendar dates. Northern: Spring Mar 1, Summer Jun 1, Autumn Sep 1, Winter Dec 1. Southern hemisphere is offset by 6 months. |

## Sensors

The integration creates **8 sensors**, all grouped under a single device:

### Current Season

| Property | Value |
|----------|-------|
| Entity ID | `sensor.{name}_current_season` |
| States | `spring`, `summer`, `autumn`, `winter` |
| Device Class | `enum` |
| Icon | Dynamic based on season |

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `mode` | `astronomical` or `meteorological` |
| `hemisphere` | `northern` or `southern` |
| `season_age` | Days since the current season started |

### Equinox & Solstice Sensors

Four timestamp sensors showing the **next occurrence** of each event:

| Entity ID | Event | Icon |
|-----------|-------|------|
| `sensor.{name}_spring_equinox` | Spring Equinox | `mdi:flower` |
| `sensor.{name}_summer_solstice` | Summer Solstice | `mdi:white-balance-sunny` |
| `sensor.{name}_autumn_equinox` | Autumn Equinox | `mdi:leaf` |
| `sensor.{name}_winter_solstice` | Winter Solstice | `mdi:snowflake` |

Each sensor has:
- **State**: ISO 8601 timestamp (UTC)
- **Device Class**: `timestamp`
- **Attribute `days_until`**: Days remaining until the event (0 on the day itself)
- **Attribute `last_start`**: Date of the most recent past occurrence (ISO date format)

After an event occurs, the sensor automatically shows the next year's date.

**Note:** The timestamps reflect the configured calculation mode (see [Understanding Timezone Handling](#understanding-timezone-handling) for details).

### Next Season Change

| Property | Value |
|----------|-------|
| Entity ID | `sensor.{name}_next_season_change` |
| Device Class | `timestamp` |
| Icon | `mdi:timelapse` |

Shows when the next season will begin and which season it will be.

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `days_until` | Days until the next season starts |
| `event_type` | `spring`, `summer`, `autumn`, or `winter` |

### Daylight Trend

| Property | Value |
|----------|-------|
| Entity ID | `sensor.{name}_daylight_trend` |
| States | `days_getting_longer`, `days_getting_shorter`, `solstice_today` |
| Device Class | `enum` |
| Icon | Dynamic based on trend |

This sensor indicates whether days are currently getting longer or shorter based on the position between solstices.

### Next Daylight Trend Change

| Property | Value |
|----------|-------|
| Entity ID | `sensor.{name}_next_daylight_trend_change` |
| Device Class | `timestamp` |
| Icon | `mdi:sun-clock` |

Shows when the daylight trend will reverse (the next solstice).

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `days_until` | Days until the next solstice |
| `event_type` | `summer_solstice` or `winter_solstice` |

## Technical Details

| Property | Value |
|----------|-------|
| Update Interval | Once per day |
| IoT Class | `calculated` |
| Calculation Library | [PyEphem](https://rhodesmill.org/pyephem/) |
| Platforms | Sensor |

## Understanding Timezone Handling

All timestamps are stored in **UTC**, following Home Assistant's internal design principle. Home Assistant automatically converts these to your local timezone for display in the frontend.

### What This Means in Practice

**Astronomical Mode:**
The Spring Equinox 2026 occurs at `2026-03-20T14:46:00+00:00` (UTC). If you're in Central European Time, you'll see `15:46` (CET) or `16:46` (CEST) - this is the exact moment the event occurs at your location.

**Meteorological Mode:**
Season dates are stored as midnight UTC on the first day of the month. For example, meteorological spring is stored as `2026-03-01T00:00:00+00:00`. In Central European Time, this displays as `01:00` (CET) or `02:00` (CEST).

### Using Timestamps in Automations

When you use a timestamp sensor as an automation trigger, it fires at the stored UTC moment:

| Mode | Stored (UTC) | Display (CET) | Automation triggers |
|------|--------------|---------------|---------------------|
| Astronomical | `2026-03-20T14:46:00Z` | 15:46 | 15:46 local time |
| Meteorological | `2026-03-01T00:00:00Z` | 01:00 | 01:00 local time |

This UTC-based approach ensures consistency: the same timestamp always refers to the same moment in time, regardless of timezone changes or daylight saving time transitions.

## Localization

The integration supports multiple languages through Home Assistant's translation system. All sensor names and states are translated.

**Currently supported languages:**

- English (fallback)
- German (Deutsch)
- Dutch (Nederlands)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the [Home Assistant Season Integration](https://www.home-assistant.io/integrations/season/)
- Astronomical calculations powered by [PyEphem](https://rhodesmill.org/pyephem/)
- Development assisted by [Claude](https://claude.ai/) (Anthropic)
