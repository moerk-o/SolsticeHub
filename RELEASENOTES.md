> ## ⚠️ Please read before updating — manual step required
>
> **SolsticeHub is the renamed successor of *Solstice Season*.** Because the
> Home Assistant domain changed, your existing devices **cannot** be migrated
> automatically. After updating you must **remove the old "Solstice Season"
> integration and add "SolsticeHub" anew**, then repoint your automations and
> dashboards. Long-term statistics / history of the old entities are **not**
> carried over. Details under **Breaking Changes** below.

### ✨ New Features

- **Device types**: when adding the integration you now choose which calendar
  you want:
  - **Four Seasons** – the familiar spring/summer/autumn/winter. Pick
    *astronomical* (seasons start at the equinoxes and solstices) or
    *meteorological* (fixed calendar dates), for either hemisphere.
  - **Cross-Quarter / Celtic** – the Celtic *Wheel of the Year*: eight seasonal
    festivals (Imbolc, Beltane, Lughnasadh, Samhain and the solstices/equinoxes)
    that fall midway between the seasons. Pick astronomical midpoints or
    traditional fixed dates, and system-language or Celtic names. ([#7](https://github.com/moerk-o/SolsticeHub/issues/7))
  - **Chinese Solar Terms** – the 24 *solar terms* of the traditional East Asian
    calendar, which divide the year by the sun's position. Pick all 24 terms or
    just the 8 major ones, with system-language, Pinyin or Hanzi names.
- **Daylight trend on every calendar**: `daylight_trend` and
  `next_daylight_trend_change` are now part of every device, alongside a
  diagnostic `solar_longitude` sensor (disabled by default).
- **`season_progress`** attribute on the current-season sensor.
- **`last_start` attribute** on the timestamp sensors — when the current period
  last began. ([#4](https://github.com/moerk-o/SolsticeHub/issues/4))
- **Simpler setup**: you pick the device type and name the device in Home
  Assistant's standard final step.

### 🐞 Bug Fixes

- Sensors now update exactly at each change (and at local midnight) instead of
  on a 24-hour timer from the last restart, so changes are reflected on time.
  ([#6](https://github.com/moerk-o/SolsticeHub/issues/6))

### 📝 Documentation

- For the complete v1.x release history (as *Solstice Season*), see
  [RELEASENOTES_v1.md](RELEASENOTES_v1.md).

### ⚠️ Breaking Changes

**The integration was renamed from *Solstice Season* to *SolsticeHub*.** The
domain changed from `solstice_season` to `solsticehub` (and the repository moved
to [`SolsticeHub`](https://github.com/moerk-o/SolsticeHub)), so Home Assistant
treats it as a new integration and **cannot migrate your configuration
automatically**. A one-time manual switch is required:

1. *(Optional)* Note your current device type and options, and which automations
   or dashboards use the old entities.
2. Update to v2.0.0 (HACS shows it as an update of the same repository).
3. Remove the old **Solstice Season** integration: Settings → Devices & Services
   → *Solstice Season* → ⋮ → Delete.
4. Restart Home Assistant.
5. Add **SolsticeHub**: Settings → Devices & Services → *Add Integration* →
   *SolsticeHub*, then choose your device type and options.
6. Repoint your automations and dashboards to the new entities.

Your old entities' **long-term statistics / history are not carried over**.

**Full Changelog**: https://github.com/moerk-o/SolsticeHub/compare/v1.5.1...v2.0.0
