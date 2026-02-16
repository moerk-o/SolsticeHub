# Issue #4: Attribute Cleanup für v2.0

## Übersicht

Bereinigung der `current_season` Sensor-Attribute und Verbesserung der Timestamp-Sensoren.

GitHub Issue: https://github.com/moerk-o/ha-solstice_season/issues/4

---

## Änderungen

### 1. `*_start` Attribute ENTFERNEN

**Von `current_season` Sensor entfernen:**
- [ ] `spring_start`
- [ ] `summer_start`
- [ ] `autumn_start`
- [ ] `winter_start`

**Begründung:** Redundant mit den dedizierten Timestamp-Sensoren (`spring_equinox`, `summer_solstice`, etc.)

**Dateien:**
- `sensor.py` - Attribute aus `extra_state_attributes_fn` entfernen
- `calculations.py` - Felder aus `SeasonData` TypedDict entfernen

---

### 2. `season_age` BEHALTEN

**Status:** Keine Änderung nötig

**Aktuell auf `current_season`:**
- `season_age: 57` (Tage seit Start der aktuellen Jahreszeit)

---

### 3. `last_start` Attribut NEU HINZUFÜGEN

**Auf jeden Timestamp-Sensor hinzufügen:**

| Sensor | Neues Attribut | Beispiel (Feb 2026) |
|--------|----------------|---------------------|
| `spring_equinox` | `last_start: 2025-03-20` | Letzter Frühlingsanfang |
| `summer_solstice` | `last_start: 2025-06-21` | Letzter Sommeranfang |
| `autumn_equinox` | `last_start: 2025-09-22` | Letzter Herbstanfang |
| `winter_solstice` | `last_start: 2025-12-21` | Letzter Winteranfang |

**Dateien:**
- `sensor.py` - `extra_state_attributes_fn` für jeden Timestamp-Sensor erweitern
- `calculations.py` - `previous_*` Felder zu `SeasonData` hinzufügen

---

## Ergebnis nach Implementierung

### `current_season` Sensor (schlank)
```
state: winter
Attribute:
  season_age: 57
  mode: astronomical
  hemisphere: northern
```

### `winter_solstice` Sensor (vollständig)
```
state: 2026-12-21 (nächster)
Attribute:
  days_until: 307
  last_start: 2025-12-21 (letzter)
```

---

## Implementierungsreihenfolge

### Teil 1: `last_start` Attribut hinzufügen
1. [x] `calculations.py` - `previous_*` Felder berechnen und hinzufügen
2. [x] `sensor.py` - `last_start` Attribut zu Timestamp-Sensoren hinzufügen
3. [x] Tests für `previous_*` Felder hinzufügen

### Teil 2: `*_start` Attribute entfernen (separater Commit)
4. [x] `sensor.py` - `*_start` Attribute von `current_season` entfernen
5. [x] `calculations.py` - Alte `*_start` Felder aus TypedDict entfernen
6. [x] Tests anpassen (keine Änderungen nötig - alle 42 Tests bestanden)
7. [x] README.md aktualisiert
8. [ ] Issue #4 schließen (via Commit)
