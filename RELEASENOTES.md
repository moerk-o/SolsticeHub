### ⚠️ Breaking Changes

- **The integration was renamed from *Solstice Season* to *SolsticeHub*.**
  - The domain changed from `solstice_season` to `solsticehub`, and the
    repository moved to [`SolsticeHub`](https://github.com/moerk-o/SolsticeHub).
  - Home Assistant cannot migrate config entries across domains, so this is a
    one-time manual step: **remove the old "Solstice Season" integration and add
    "SolsticeHub" anew** (Settings → Devices & Services). Your automations that
    reference the old entities need to be repointed to the new ones.

### ✨ New Features

- **Device types**: when adding the integration you now choose a device type:
  - **Four Seasons** – the classic astronomical/meteorological seasons.
  - **Cross-Quarter / Celtic** – the Wheel of the Year (Imbolc, Beltane, …),
    astronomical midpoints or traditional fixed dates, system or Celtic naming.
  - **Chinese Solar Terms** – the 24 solar terms (or the 8 major ones), with
    system, Pinyin or Hanzi naming.
- **Daylight trend on every calendar**: `daylight_trend` and
  `next_daylight_trend_change` are now part of every device, alongside a
  diagnostic `solar_longitude` sensor (disabled by default).
- **`season_progress`** attribute on the current-season sensor.

### 🗑️ Removed

- The separate **Base Data** device type. Its sensors are now included in every
  calendar device, so a single device gives you both the calendar and the
  daylight trend.

### 📝 Documentation

- For the complete v1.x release history (as *Solstice Season*), see
  [RELEASENOTES_v1.md](RELEASENOTES_v1.md).

**Full Changelog**: https://github.com/moerk-o/SolsticeHub/compare/v1.5.1...v2.0.0
