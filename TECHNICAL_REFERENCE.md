# Technical Reference: Home Assistant Integration `solstice_season`

**Version:** 1.5.0
**Date:** December 19, 2025
**Target Platform:** Home Assistant Custom Integration
**Development Language:** English (code, comments, variables)
**Translations:** English (fallback), German, Dutch
**Repository:** https://github.com/moerk-o/ha-solstice_season

---

## 1. Project Overview

### 1.1 Purpose

The `solstice_season` integration provides precise, day-precise seasonal information as sensors in Home Assistant. Compared to the existing `season` integration, it offers:

- Current season
- Exact timestamps for all four seasonal transitions (solstices & equinoxes) including countdown
- Next season change with date and countdown
- Choice between astronomical or meteorological (calendar-based) calculation
- Daylight trend sensor (are days getting longer or shorter?) including countdown to next trend change
- Support for Northern and Southern hemispheres
- Full multilingual support via the HA translation system
- Support for multiple instances (e.g., for different locations or calculation modes)

### 1.2 Inspiration & Reference

The integration is based on the existing `season` integration in Home Assistant Core:

- **Documentation:** https://www.home-assistant.io/integrations/season/
- **Source Code:** https://github.com/home-assistant/core/tree/dev/homeassistant/components/season

### 1.3 Naming Convention

- **Domain:** `solstice_season`
- **Entity Prefix:** user-defined name in ConfigFlow (e.g., "Home" → `sensor.home_*`)

---

## 2. Calculation Fundamentals

### 2.1 Astronomical vs. Meteorological Mode

The integration offers two different calculation modes that follow fundamentally different approaches to defining seasons.

#### Astronomical Mode

The astronomical mode is based on the actual position of the Earth relative to the Sun. The Earth's axis is tilted by approximately 23.4° – this tilt is the reason we have seasons at all. Throughout the year, this changes the angle at which sunlight hits different regions of the Earth.

**The four key astronomical events:**

| Event | Time Period | What Happens |
|-------|-------------|--------------|
| **March Equinox** | approx. March 19-21 | The Sun is positioned directly above the equator. Day and night are approximately equal length everywhere on Earth. |
| **June Solstice** | approx. June 20-22 | The Sun reaches its northernmost point. Longest day in the Northern Hemisphere, shortest in the Southern Hemisphere. |
| **September Equinox** | approx. September 21-23 | The Sun is again positioned directly above the equator. Day and night are approximately equal length again. |
| **December Solstice** | approx. December 20-23 | The Sun reaches its southernmost point. Shortest day in the Northern Hemisphere, longest in the Southern Hemisphere. |

The exact times of these events vary by a few hours each year, as a solar year is not exactly 365 days. The integration calculates these times to the minute using the PyEphem library.

#### Meteorological Mode

Meteorologists and climate scientists use a simplified approach: seasons always begin on the 1st of the respective month. This has practical reasons – it significantly simplifies statistical analysis and comparison of climate data across years.

**Meteorological season boundaries:**

| Season | Northern Hemisphere | Southern Hemisphere |
|--------|---------------------|---------------------|
| Spring | March 1 | September 1 |
| Summer | June 1 | December 1 |
| Autumn | September 1 | March 1 |
| Winter | December 1 | June 1 |

### 2.2 Hemisphere Mapping

Due to the tilt of the Earth's axis, the Northern and Southern Hemispheres experience opposite seasons. When it's summer in the Northern Hemisphere, it's winter in the Southern Hemisphere – and vice versa.

The astronomical events themselves are globally identical (the June Solstice occurs at the same moment worldwide), but their **seasonal meaning** differs:

| Astronomical Event | Northern Hemisphere | Southern Hemisphere |
|--------------------|---------------------|---------------------|
| March Equinox | Start of Spring | Start of Autumn |
| June Solstice | Start of Summer | Start of Winter |
| September Equinox | Start of Autumn | Start of Spring |
| December Solstice | Start of Winter | Start of Summer |

### 2.3 The Daylight Trend

Regardless of seasonal classification, there is a physical reality: after the December Solstice, days get longer; after the June Solstice, days get shorter. This applies equally to both hemispheres – it is a direct consequence of Earth's orbit around the Sun.

The calendar dates of June 1 or December 1 have no influence on actual daylight duration.

---

## 3. Sensors in Detail

The integration provides **8 sensors**. All sensors belong to a common device that carries the user-defined name.

### 3.1 `current_season` – Current Season

#### Description

Shows the currently active season.

#### Calculation Logic

The current season is calculated based on the configured mode – see [Section 2.1](#21-astronomical-vs-meteorological-mode) for details on the differences.

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_current_season` |
| **Device Class** | `enum` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `spring` | enum | `mdi:flower` |
| `summer` | enum | `mdi:white-balance-sunny` |
| `autumn` | enum | `mdi:leaf` |
| `winter` | enum | `mdi:snowflake` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `mode` | `str` | `astronomical` or `meteorological` – the selected calculation mode |
| `hemisphere` | `str` | `northern` or `southern` – the selected hemisphere |
| `spring_start` | `str` (ISO 8601) | Date of spring start in the current calendar year |
| `summer_start` | `str` (ISO 8601) | Date of summer start in the current calendar year |
| `autumn_start` | `str` (ISO 8601) | Date of autumn start in the current calendar year |
| `winter_start` | `str` (ISO 8601) | Date of winter start in the current calendar year |
| `season_age` | `int` | Days since the start of the current season (correct across year boundaries) |

*Note: The `*_start` attributes always refer to the current calendar year. On January 1st, for example, `winter_start` jumps to the December date of the new year, even though the current winter started in the previous year. For reliably determining how long the current season has been ongoing, use `season_age` instead.*

---

### 3.2 `spring_equinox` – Start of Spring

#### Description

Shows the timestamp of the next start of spring. After the event occurs, the sensor automatically rolls over to the next year.

#### Calculation Logic

Depending on the hemisphere, the March Equinox (North) or September Equinox (South) is used – see [Section 2.2](#22-hemisphere-mapping).

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_spring_equinox` |
| **Device Class** | `timestamp` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `<sensor value>` | string (ISO 8601) | `mdi:flower` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `days_until` | `int` | Remaining days until the event (0 on the day itself) |

---

### 3.3 `summer_solstice` – Start of Summer

#### Description

Shows the timestamp of the next start of summer. After the event occurs, the sensor automatically rolls over to the next year.

#### Calculation Logic

Depending on the hemisphere, the June Solstice (North) or December Solstice (South) is used – see [Section 2.2](#22-hemisphere-mapping).

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_summer_solstice` |
| **Device Class** | `timestamp` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `<sensor value>` | string (ISO 8601) | `mdi:white-balance-sunny` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `days_until` | `int` | Remaining days until the event |

---

### 3.4 `autumn_equinox` – Start of Autumn

#### Description

Shows the timestamp of the next start of autumn. After the event occurs, the sensor automatically rolls over to the next year.

#### Calculation Logic

Depending on the hemisphere, the September Equinox (North) or March Equinox (South) is used – see [Section 2.2](#22-hemisphere-mapping).

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_autumn_equinox` |
| **Device Class** | `timestamp` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `<sensor value>` | string (ISO 8601) | `mdi:leaf` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `days_until` | `int` | Remaining days until the event |

---

### 3.5 `winter_solstice` – Start of Winter

#### Description

Shows the timestamp of the next start of winter. After the event occurs, the sensor automatically rolls over to the next year.

#### Calculation Logic

Depending on the hemisphere, the December Solstice (North) or June Solstice (South) is used – see [Section 2.2](#22-hemisphere-mapping).

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_winter_solstice` |
| **Device Class** | `timestamp` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `<sensor value>` | string (ISO 8601) | `mdi:snowflake` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `days_until` | `int` | Remaining days until the event |

---

### 3.6 `daylight_trend` – Daylight Trend

#### Description

Shows whether the days are currently getting longer or shorter.

#### Calculation Logic

This sensor **always uses astronomical solstices**, even in meteorological mode – see [Section 2.3](#23-the-daylight-trend) for the reasoning.

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_daylight_trend` |
| **Device Class** | `enum` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `days_getting_longer` | enum | `mdi:arrow-right-bold-outline` |
| `days_getting_shorter` | enum | `mdi:arrow-left-bold-outline` |
| `solstice_today` | enum | `mdi:arrow-left-right-bold-outline` |

#### Attributes

No additional attributes.

---

### 3.7 `next_daylight_trend_change` – Next Trend Change

#### Description

Shows the timestamp of the next solstice, as it marks the turning point in the daylight trend.

#### Calculation Logic

This sensor **always uses astronomical solstices**, even in meteorological mode – see [Section 2.3](#23-the-daylight-trend).

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_next_daylight_trend_change` |
| **Device Class** | `timestamp` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `<sensor value>` | string (ISO 8601) | `mdi:sun-clock` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `days_until` | `int` | Remaining days until the next solstice |
| `event_type` | `str` | `summer_solstice` or `winter_solstice` (relative to the hemisphere) |

---

### 3.8 `next_season_change` – Next Season Change

#### Description

Shows the timestamp of the next season change and which season will begin.

#### Calculation Logic

Uses the configured mode (astronomical or meteorological) – see [Section 2.1](#21-astronomical-vs-meteorological-mode).

#### State Values and Icons

| Property | Value |
|----------|-------|
| **Entity ID Pattern** | `sensor.{prefix}_next_season_change` |
| **Device Class** | `timestamp` |
| **State Class** | `None` |

| State | Format | Icon |
|-------|--------|------|
| `<sensor value>` | string (ISO 8601) | `mdi:timelapse` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `days_until` | `int` | Remaining days until the next season change |
| `event_type` | `str` | `spring`, `summer`, `autumn`, or `winter` – the upcoming season |

---

## 4. ConfigFlow

### 4.1 Overview

The integration is configured exclusively via the UI (no YAML support). The ConfigFlow consists of a single step.

### 4.2 Configuration Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | `str` | Yes | `Home` | Instance name, becomes the entity prefix |
| `hemisphere` | `select` | Yes | Pre-filled from Home Assistant Home location | Hemisphere: `northern` or `southern` |
| `mode` | `select` | Yes | `astronomical` | Calculation mode: `astronomical` or `meteorological` |

---

## 5. Technical Reference

This chapter contains technical implementation details for developers.

### 5.1 Project Language & Code Style

All development is done in **English** – code, comments, commit messages, issues, release notes, and documentation. This enables global usage and contributions.

Development should follow these guidelines:

- **Language:** English for all variables, functions, comments, docstrings
- **Type Hints:** Use everywhere
- **Docstrings:** Google-Style
- **Formatting:** Black, isort
- **Linting:** Pylint, Flake8

### 5.2 HACS Distribution

This integration is listed in [HACS](https://hacs.xyz/) (Home Assistant Community Store) for easy installation and updates. To maintain HACS compatibility, the following requirements must be met:

- **Repository structure:** `custom_components/<domain>/` with valid `manifest.json`
- **hacs.json:** Configuration file in repository root
- **GitHub Releases:** Versions are distributed via GitHub releases (not branches/tags alone)
- **Validation:** The `validate.yaml` workflow runs Hassfest and HACS validation on every push/PR

**Reference:** [HACS Developer Documentation](https://hacs.xyz/docs/publish/start)

### 5.3 Unique ID & Duplicate Prevention

The Unique ID is based on the slugified name:
```python
unique_id = slugify(user_input[CONF_NAME])
```

This allows multiple instances with different names while preventing duplicates with the same name.

### 5.4 ConfigFlow Process

```
┌─────────────────────────────────────┐
│         async_step_user             │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Name: [Home____________]    │    │
│  │                             │    │
│  │ Hemisphere: [Northern    ▼] │    │
│  │             ├─Northern      │    │
│  │             └─Southern      │    │
│  │                             │    │
│  │ Mode: [Astronomical     ▼]  │    │
│  │       ├─Astronomical        │    │
│  │       └─Meteorological      │    │
│  └─────────────────────────────┘    │
│                                     │
│           [Submit]                  │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      async_create_entry             │
│                                     │
│  - Set Unique ID                    │
│  - Create Config Entry              │
│  - Start Integration Setup          │
└─────────────────────────────────────┘
```

### 5.5 File Structure

```
solstice_season/
├── custom_components/
│   └── solstice_season/
│       ├── <Python modules>     # Integration source code
│       └── translations/
│           └── <Language files> # Translations (en.json, de.json, nl.json, ...)
├── assets/
│   └── <Graphics>               # Icons and logos (for HA Brands, HACS)
├── .github/
│   └── workflows/
│       └── <GitHub Actions>     # CI/CD Workflows (validation, releases)
└── <Project root>               # Configuration, documentation, license
```

### 5.6 Dependencies

#### External Libraries

| Library | Usage | In HA Core? |
|---------|-------|-------------|
| `ephem` | Calculation of solstices/equinoxes | ✅ Yes (used by season integration) |

The `ephem` library (PyEphem) is also used by the Home Assistant Core `season` integration. It calculates astronomical events locally without internet connection.

**Reference:** https://rhodesmill.org/pyephem/

#### Home Assistant Helpers

| Import | Usage |
|--------|-------|
| `homeassistant.core` | HomeAssistant instance |
| `homeassistant.config_entries` | ConfigEntry, ConfigFlow |
| `homeassistant.components.sensor` | SensorEntity, SensorDeviceClass |
| `homeassistant.helpers.update_coordinator` | DataUpdateCoordinator, CoordinatorEntity |
| `homeassistant.helpers.device_registry` | DeviceInfo for device grouping |
| `homeassistant.helpers.selector` | UI selectors for ConfigFlow |
| `homeassistant.util.dt` | Time functions (UTC handling) |
| `homeassistant.util.slugify` | Normalization of names to IDs |

### 5.7 DataUpdateCoordinator

The integration uses the Home Assistant `DataUpdateCoordinator` for centralized data management. All 8 sensors obtain their data from a single data source managed by the coordinator.

**Update Interval:** 24 hours, starting from the time of HA start or integration loading. Values only change daily, more frequent updates would be pointless.

**Calculation:** The calculation logic (`calculate_season_data`) is executed in an executor to avoid blocking the event loop. The function receives `hemisphere` and `mode` from the Config Entry.

### 5.8 Device Registration

All 8 sensors of an integration instance are grouped under a common device to logically organize them in the Home Assistant UI.

| Field | Value |
|-------|-------|
| **Name** | user-defined name (e.g., "Home") |
| **Manufacturer** | "Solstice Season" |
| **Model** | Dynamic: "Astronomical Calculator" or "Meteorological Calculator" depending on mode |
| **Software Version** | Version from `manifest.json` |
| **Identifier** | `entry_id` of the Config Entry |

### 5.9 Time Calculation

All times are calculated and stored in **UTC** – this is HA standard. Home Assistant automatically converts these to the user's local timezone for display. See [HA DateTime Helpers](https://developers.home-assistant.io/docs/core/helpers/datetime/).

### 5.10 Calculation Logic

The technical fundamentals (astronomical vs. meteorological, hemisphere mapping, daylight trend) are documented in [Chapter 2 – Calculation Fundamentals](#2-calculation-fundamentals).

#### ephem Library

The `ephem` library calculates the exact times of the four key astronomical events. Results are converted to UTC-aware datetimes.

| ephem Function | Event |
|----------------|-------|
| `next_vernal_equinox` | March Equinox |
| `next_summer_solstice` | June Solstice |
| `next_autumnal_equinox` | September Equinox |
| `next_winter_solstice` | December Solstice |

### 5.11 Translations

The integration uses the HA translation system with `translation_key` at sensor level. Currently supported languages: **English** (fallback), **German**, **Dutch**.

#### File Format

Translations are stored in the `translations/` folder as JSON files. One file per language with the **ISO 639-1 language code** as filename:

- `translations/en.json` – English (fallback)
- `translations/de.json` – German
- `translations/nl.json` – Dutch
- `translations/fr.json` – French (example for new language)

The structure within the JSON file must be identical for all languages – only the text values are translated.

#### Translated Sections

| JSON Path | Description |
|-----------|-------------|
| `config.step.user` | ConfigFlow dialog (title, description, field names) |
| `config.error` / `config.abort` | Error messages in ConfigFlow |
| `selector.hemisphere` / `selector.mode` | Dropdown options |
| `entity.sensor.<key>.name` | Sensor names |
| `entity.sensor.<key>.state` | State values for ENUM sensors |

#### Adding a New Language

1. Copy existing file: `cp translations/en.json translations/fr.json`
2. Translate all text values (keep keys unchanged)
3. Restart Home Assistant

**Reference:** [HA Internationalization](https://developers.home-assistant.io/docs/internationalization/core/)

### 5.12 manifest.json

The `manifest.json` defines the integration's metadata. Relevant fields:

| Field | Value | Explanation |
|-------|-------|-------------|
| `domain` | `solstice_season` | Unique identifier of the integration |
| `config_flow` | `true` | Integration uses UI configuration |
| `integration_type` | `service` | No hardware, pure service |
| `iot_class` | `calculated` | Data is calculated locally, no network required |
| `requirements` | `["ephem>=4.1.0"]` | PyEphem for astronomical calculations |
| `version` | `x.y.z` | Current version (updated on releases) |

**Reference:** [HA Integration Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/)

---

## 6. Resources

#### Home Assistant Development

| Topic | Link |
|-------|------|
| Developer Documentation (Getting Started) | https://developers.home-assistant.io/ |
| Integration Manifest | https://developers.home-assistant.io/docs/creating_integration_manifest/ |
| ConfigFlow | https://developers.home-assistant.io/docs/config_entries_config_flow_handler/ |
| Sensor Entity | https://developers.home-assistant.io/docs/core/entity/sensor/ |
| Internationalization | https://developers.home-assistant.io/docs/internationalization/core/ |
| Translation Keys | https://developers.home-assistant.io/docs/internationalization/core/#name-of-entities |
| DataUpdateCoordinator | https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities |
| DateTime Helpers | https://developers.home-assistant.io/docs/core/helpers/datetime/ |

#### Astronomical References

| Topic | Link |
|-------|------|
| Season (Wikipedia EN) | https://en.wikipedia.org/wiki/Season |
| Solstice (Wikipedia EN) | https://en.wikipedia.org/wiki/Solstice |
| Equinox (Wikipedia EN) | https://en.wikipedia.org/wiki/Equinox |
| PyEphem Library | https://rhodesmill.org/pyephem/ |

#### Reference Integrations

| Integration | Link | Relevance |
|-------------|------|-----------|
| Season (HA Core) | https://github.com/home-assistant/core/tree/dev/homeassistant/components/season | Direct inspiration |
| Sun (HA Core) | https://github.com/home-assistant/core/tree/dev/homeassistant/components/sun | Astronomical calculations |
| Moon (HA Core) | https://github.com/home-assistant/core/tree/dev/homeassistant/components/moon | Similar sensor structure |

#### Python References

| Topic | Link |
|-------|------|
| datetime Module | https://docs.python.org/3/library/datetime.html |
| typing Module | https://docs.python.org/3/library/typing.html |

---

## 7. Release Process

### Before Release

- All changes are merged into `main`
- Bump version in `custom_components/solstice_season/manifest.json`
- Update `RELEASENOTES.md`:
  - Insert new release content at the top (without `# vX.Y.Z` heading – see note below)
  - Add `# vX.Y.Z` heading above the previous release content
  - Link issue numbers: `[#123](https://github.com/moerk-o/ha-solstice_season/issues/123)`
  - Use consistent section headers and icons from previous releases:
    - ✨ New Features
    - 🐞 Bug Fixes
    - 🔧 Infrastructure
    - 📝 Documentation
    - 💬 Feedback Needed!
  - For new section types, discuss first before adding
- Update README.md if needed (document new features/attributes)
- Commit and push changes

**Note on version headings:** GitHub displays the release title (from `--title`) automatically above the release notes content. HACS uses this for the update dialog. To avoid duplicate version headings, the current release section should not start with a `# vX.Y.Z` heading – it would appear twice (once from `--title`, once from the markdown).

We explicitly specify `--title` rather than relying on GitHub's default behavior (using the tag name) to ensure consistent display regardless of any future GitHub changes.

### Create Release

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASENOTES.md
```

### After Release

- GitHub workflow (`release.yml`) automatically creates `solstice_season.zip` and attaches it to the release
- Verify ZIP is present in the release assets

### Workflows

The following GitHub Actions workflows run automatically:

- **validate.yaml** - Runs on every push/PR, validates Home Assistant (Hassfest) and HACS compatibility. Required for HACS listing.
- **release.yml** - Runs when a release is published, creates and uploads the ZIP asset.

---

## 8. Version History

This table provides a technical overview of changes per version. For **user-friendly release notes** with detailed descriptions, issue links, and categorization, see [`RELEASENOTES.md`](RELEASENOTES.md).

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-02 | Initial implementation |
| 1.1.0 | 2025-12-02 | Switch from astral to ephem library |
| 1.1.1 | 2025-12-02 | Bugfix: Meteorological mode now uses calendar dates for timestamps |
| 1.2.0 | 2025-12-09 | New sensor: `next_season_change` |
| 1.3.0 | 2025-12-12 | Dutch translation added |
| 1.4.0 | 2025-12-17 | Hemisphere auto-detection based on Home location; Device version shows integration version |
| 1.5.0 | 2025-12-19 | New attribute `season_age`; Bugfix: Daylight trend in meteorological mode (#3); Bugfix: Device model shows correct mode (#5) |

---

*This technical reference serves as the complete specification and documentation of the `solstice_season` Home Assistant integration.*
