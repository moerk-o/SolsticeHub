# Technical Reference: SolsticeHub

**Version:** 2.0.0
**Stand:** June 2026
**Target Platform:** Home Assistant Custom Integration
**Development Language:** English (code, comments, variables)
**Translations:** English (fallback), German, Dutch
**Repository:** https://github.com/moerk-o/SolsticeHub

---

## 1. Project Overview

### 1.1 Purpose

SolsticeHub provides sun-based calendar information as Home Assistant sensors.
It goes beyond the core `season` integration by offering several calendar
systems, precise event timestamps, countdowns and daylight-trend tracking — all
calculated locally with PyEphem.

SolsticeHub is the renamed successor of the **Solstice Season** integration
(domain `solstice_season`, v1.x). See the ADR in [5.12](#512-adr-domain-rename-to-solsticehub).

### 1.2 Device Types

Each config entry creates exactly one device of a chosen type:

| Device type (`device_type`) | Domain value | Description |
|-----------------------------|--------------|-------------|
| Four Seasons | `four_seasons` | Astronomical or meteorological seasons |
| Cross-Quarter / Celtic | `cross_quarter` | Wheel of the Year (eight festivals) |
| Chinese Solar Terms | `chinese` | 24 (or 8 major) solar terms |

Every device additionally exposes the **shared base-data sensors**
(`solar_longitude`, `daylight_trend`, `next_daylight_trend_change`) — see
[5.11](#511-adr-base-data-folded-into-every-calendar-device).

### 1.3 Naming Convention

- **Domain:** `solsticehub`
- **Entity prefix:** the user-defined device name (e.g. "Home" → `sensor.home_*`)

---

## 2. Calculation Fundamentals

### 2.1 Astronomical vs. Meteorological (Four Seasons)

Astronomical seasons begin at the exact equinoxes/solstices (PyEphem, to the
minute; dates vary by a few hours each year). Meteorological seasons begin on
fixed calendar dates (1 March/June/September/December), offset by six months in
the southern hemisphere.

### 2.2 Hemisphere Mapping

The astronomical events are global, but their seasonal meaning is reversed
between hemispheres:

| Event | Northern | Southern |
|-------|----------|----------|
| March Equinox | Spring | Autumn |
| June Solstice | Summer | Winter |
| September Equinox | Autumn | Spring |
| December Solstice | Winter | Summer |

### 2.3 Daylight Trend

After the December solstice days get longer; after the June solstice they get
shorter — physically true for both hemispheres (the southern interpretation is
inverted). The daylight trend therefore always uses the astronomical solstices,
regardless of the configured calendar or mode.

### 2.4 Cross-Quarter Days

The four cross-quarter points sit midway between the solstices and equinoxes. In
**astronomical** mode they are found by solving for the Sun's ecliptic longitude
(315°, 45°, 135°, 225°) via binary search; in **traditional** mode the fixed
Celtic dates (1 Feb/May/Aug/Nov) are used. Solstices/equinoxes are always
astronomical.

### 2.5 Chinese Solar Terms

The 24 solar terms are 15°-spaced ecliptic-longitude points, found by the same
binary search. The "8 major" scope keeps only the seasonal markers (the four
"start of season" terms plus the equinoxes/solstices).

---

## 3. Entities

### 3.1 Shared base-data sensors (all device types)

| Key | Device class | Notes |
|-----|--------------|-------|
| `solar_longitude` | — (measurement, °) | Diagnostic, `entity_registry_enabled_default=False` |
| `daylight_trend` | enum | `days_getting_longer` / `days_getting_shorter` / `solstice_today` |
| `next_daylight_trend_change` | timestamp | Attributes: `days_until`, `event_type` |

### 3.2 Four Seasons

| Key | Device class | Attributes |
|-----|--------------|-----------|
| `current_season` | enum | `mode`, `hemisphere`, `season_age`, `season_progress` |
| `spring_equinox` / `summer_solstice` / `autumn_equinox` / `winter_solstice` | timestamp | `days_until`, `last_start` |
| `next_season_change` | timestamp | `days_until`, `event_type` |

### 3.3 Cross-Quarter

| Key | Device class | Attributes |
|-----|--------------|-----------|
| `current_period` | enum | `mode`, `period_age`, `events` |
| `next_period_change` | timestamp | `days_until`, `event_type` |

### 3.4 Chinese Solar Terms

| Key | Device class | Attributes |
|-----|--------------|-----------|
| `current_term` | enum | `scope`, `term_age`, `events` |
| `next_term_change` | timestamp | `days_until`, `event_type` |

---

## 4. ConfigFlow

Multi-step, UI-only:

1. **user** — device type only (rendered as radio buttons).
2. Device-specific step (`four_seasons` / `cross_quarter` / `chinese`) collecting
   the options from the README configuration table. The hemisphere is fixed at
   this point (no runtime changes); Cross-Quarter and Chinese default to
   northern.

The instance name is not asked in the flow: the device name defaults to the
type-plus-mode label from `device.device_model` and the user sets it in Home
Assistant's standard final "name and assign area" step. No unique ID is set, so
multiple instances of the same type are allowed.

### 4.1 Language handling

Three independent layers, each with a different language source:

| Layer | Example | Language follows | Mechanism |
|-------|---------|------------------|-----------|
| Entity ID | `sensor.home_current_season` | none — always English | `suggested_object_id` returns the English `entity_description.key` |
| Entity display name | "Current Season" / "Aktuelle Jahreszeit" | viewing user (live) | `translation_key` + `_attr_has_entity_name` |
| Default instance name | "Four Seasons (Astronomical)" / "Vier Jahreszeiten (Astronomisch)" | system language at setup | `device_model(..., hass.config.language)`, English fallback |

`device.device_model` is the single source for both the localized default name
*and* the device `model`. The default name is built in the system language
(`hass.config.language`) because config entry titles and device names are stored
strings HA does not re-translate. The device `model`, by contrast, is a stable
identifier and is always English (`device_model` called without a language) —
like a hardware model number, it is not localized.

Entity IDs must never depend on the language: without `suggested_object_id` HA
would derive them from the translated entity name (`aktuelle_jahreszeit` on a
German system), which would break automations on a language change. Each sensor
class therefore overrides `suggested_object_id` to return the English key.

---

## 5. Technical Reference

### 5.1 Project Language & Code Style

English throughout. Type hints everywhere, Google-style docstrings, formatted
and linted with `ruff`.

### 5.2 File Structure

```
custom_components/solsticehub/
├── __init__.py                  # entry setup/unload, routes by device type
├── config_flow.py               # multi-step config flow
├── const.py                     # constants (domain, device types, keys, icons)
├── device.py                    # device_model: default name + device model label
├── calculations.py              # all astronomical calculations (pure functions)
├── manifest.json
├── coordinator.py               # Four Seasons coordinator
├── cross_quarter_coordinator.py
├── chinese_coordinator.py
├── sensor.py                    # platform entry + Four Seasons sensors
├── base_sensor.py               # shared base-data sensor descriptions (factory)
├── cross_quarter_sensor.py
├── chinese_sensor.py
├── brand/                       # local brand images (icon/logo)
└── translations/                # en, de, nl
```

### 5.3 DataUpdateCoordinator

Each device type has its own coordinator. They share one pattern: update at
local midnight (interval recomputed each run) and additionally schedule a
one-shot update at the exact next change moment via `async_track_point_in_time`.
Calculations run in the executor. `async_unload` cancels the pending event
listener.

### 5.4 Device Registration

One device per config entry, identified by `entry_id`. Model reflects the device
type and mode (e.g. "Four Seasons (Astronomical)"). Manufacturer "SolsticeHub",
software version from `manifest.json`.

### 5.5 Time Handling

All times are computed and stored in UTC; Home Assistant converts for display.

### 5.6 Brands

Brand images are bundled locally in `custom_components/solsticehub/brand/`
(supported since Home Assistant 2026.3), so no `home-assistant/brands` PR is
needed for the new domain.

### 5.7 Translations

`translation_key` per sensor; one JSON file per language under `translations/`.

### 5.8 manifest.json

`domain=solsticehub`, `integration_type=service`, `iot_class=calculated`,
`requirements=["ephem>=4.1.0"]`. Keys after `domain`/`name` are alphabetical
(hassfest).

### 5.9 Testing

100% coverage is the goal (see TESTING_GUIDE). Tests live in `tests/` and load
the integration directly from `custom_components/solsticehub` — see the ADR in
[5.13](#513-adr-test-integration-loading-single-source). A handful of defensive
"should never happen" fallback lines in `calculations.py` are unreachable by
construction and are the only intentional coverage gaps.

### 5.10 ADR: Device-type architecture

**Decision:** Each config entry creates one device with its own coordinator,
selected via a `device_type` in the config flow. No shared/singleton state.

**Context:** v2.0 introduced multiple calendar systems. An earlier prototype
(`v2-base-device` branch) used a singleton "Base Device" shared across instances,
with tracking sets and a device-registry listener.

**Why this approach:** The singleton was hard to reason about and clean up
(when is it removed? which entry owns it?). A 1:1 entry→coordinator→device model
is simple, has no cross-entry state, and needs no cleanup logic.

**Alternatives considered:**
- Singleton base device — rejected as too complex (magic creation/removal).
- One device with everything — rejected; users want to pick a calendar.

**Consequences:** Adding a calendar system is a self-contained coordinator +
sensor module + a config-flow step. Multiple devices may duplicate the shared
sun-data sensors (see 5.11).

### 5.11 ADR: Base data folded into every calendar device

**Decision:** The daylight-trend and solar-longitude sensors are part of every
calendar device, not a separate "Base Data" device.

**Context:** A short-lived v2.0 design had a separate `base_data` device type
providing `solar_longitude` / `daylight_trend` / `next_daylight_trend_change`,
factored out because the trend is calendar-independent physics.

**Why this approach:** As a separate device it was a category error in the
device-type dropdown (it is not a calendar), its only unique sensor
(`solar_longitude`) is disabled by default, and it forced users who just want
"season + is the day getting longer" to create two devices — a regression from
v1.x. Folding the trend back in restores the single-device experience.

**Consequences:** Users running several same-hemisphere calendars get duplicate
trend sensors; these are harmless and can be disabled per entity. Auto-disabling
only duplicates would require cross-entry coordination — exactly the complexity
5.10 removed — so it was rejected. The fields are computed once via
`calculate_base_data()` and merged into each coordinator's data.

### 5.12 ADR: Domain rename to solsticehub

**Decision:** Rename the integration to **SolsticeHub** (domain `solsticehub`,
repo `SolsticeHub`), shipped as a major version (v2.0.0).

**Context:** The project was renamed for branding. Home Assistant matches config
entries by domain and offers no cross-domain migration (`async_migrate_entry`
only migrates data within a domain).

**Why this approach:** A clean, consistent end state (domain, repo, display name
all aligned) is worth a one-time break, and the user base is smallest now. The
GitHub repo is renamed in place (GitHub + HACS keep redirects), preserving
stars/issues/releases and the HACS-default listing.

**Consequences:** Existing users must remove the old integration and add the new
one (documented in RELEASENOTES.md and the README migration section). The old
`custom_components/solstice_season` folder is orphaned on their systems until
removed.

### 5.13 ADR: Test integration loading (single source)

**Decision:** Tests load the integration directly from
`custom_components/solsticehub`; there is no `tests/custom_components` copy and no
sync script. `conftest.py` drops the cached top-level `custom_components` module
so Home Assistant re-resolves it as a namespace package including the project's
directory.

**Context:** `pytest-homeassistant-custom-component` ships its own
`testing_config/custom_components`, which gets cached as the top-level
`custom_components` module, so HA could not find `solsticehub`. The
TESTING_GUIDE's `tests/custom_components` copy pattern also splits coverage
across two locations (the copy executes, the source is measured → 0%).

**Why this approach:** Dropping the cache in `conftest.py` lets HA discover the
real source directory, giving a single source of truth and honest coverage. It
also removes the sync-drift risk the copy pattern warns about.

**Consequences:** This is a deliberate deviation from TESTING_GUIDE §3.7.1 (no
`tests/custom_components/`, no `sync_and_test.sh`). The rationale is the cache
collision above; the guide's mechanism does not work cleanly with this plugin
version for this project.

---

## 6. Resources

| Topic | Link |
|-------|------|
| HA Developer Docs | https://developers.home-assistant.io/ |
| ConfigFlow | https://developers.home-assistant.io/docs/config_entries_config_flow_handler/ |
| DataUpdateCoordinator | https://developers.home-assistant.io/docs/integration_fetching_data/ |
| Local brand images | https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/ |
| PyEphem | https://rhodesmill.org/pyephem/ |
| Season (HA Core) | https://github.com/home-assistant/core/tree/dev/homeassistant/components/season |

---

## 7. Release Process

See RELEASE_GUIDE. SolsticeHub is distributed via HACS as a ZIP asset
(`solsticehub.zip`, built by `release.yml`). RELEASENOTES.md is the rolling
changelog for the v2.x line; v1.x history is archived in RELEASENOTES_v1.md.

---

## 8. Version History

| Doc version | Date | Change |
|-------------|------|--------|
| 2.0.0 | June 2026 | Rewrite for SolsticeHub: device-type architecture, Cross-Quarter & Chinese calendars, shared base data, ADRs, domain rename, test-loading deviation |
| 1.5.0 | December 2025 | Final Solstice Season (v1.x) reference |
