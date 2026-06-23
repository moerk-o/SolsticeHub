# Archived v1.x release notes

> This file contains the complete release history of the v1.x line, when the
> integration was named **Solstice Season** (domain `solstice_season`). For
> v2.x onwards (**SolsticeHub**, domain `solsticehub`), see
> [RELEASENOTES.md](RELEASENOTES.md).

---

# v1.5.1

### 🐞 Bug Fixes

- **Fixed daylight trend for southern hemisphere** ([#8](https://github.com/moerk-o/ha-solstice_season/issues/8))
  - The `daylight_trend` sensor now correctly shows "days getting shorter" after the summer solstice in the southern hemisphere
  - Previously, the sensor showed the northern hemisphere perspective regardless of configuration

### 🔮 v2.0 is coming!

The next major version will include breaking changes, support for new calendar systems, and a new name for the integration.

**Get ready for SolsticeHub!**

**Full Changelog**: https://github.com/moerk-o/ha-solstice_season/compare/v1.5.0...v1.5.1

---

# v1.5.0

### ✨ New Features
- Added `season_age` attribute to current season sensor for progress tracking ([#2](https://github.com/moerk-o/ha-solstice_season/issues/2))

### 🐞 Bug Fixes
- Daylight trend now shows correct values in meteorological mode ([#3](https://github.com/moerk-o/ha-solstice_season/issues/3))
- Device model now correctly displays "Astronomical Calculator" or "Meteorological Calculator" ([#5](https://github.com/moerk-o/ha-solstice_season/issues/5))

### 📝 Documentation
- Updated README with new `season_age` attribute

### 💬 Feedback Needed!
- Considering changes to some attributes on the current_season sensor -- [please share your thoughts on issue #4](https://github.com/moerk-o/ha-solstice_season/issues/4)!

**Full Changelog**: https://github.com/moerk-o/ha-solstice_season/compare/v1.4.0...v1.5.0

---

# v1.4.0

### ✨ New Features
- Hemisphere is now pre-selected based on your Home location during setup ([#1](https://github.com/moerk-o/ha-solstice_season/issues/1))
- Device firmware version now reflects integration version

### 🔧 Infrastructure
- Switched to release asset packaging

### 📝 Documentation
- Updated README with new hemisphere-default behavior

**Full Changelog**: https://github.com/moerk-o/ha-solstice_season/compare/v1.3.0...v1.4.0
