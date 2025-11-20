# GridForge

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/gridforge?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/gridforge)

Eine **extrem schnelle** und moderne Python-Bibliothek zur Erstellung von gut formatierten Tabellen in der Konsole.

## ⚡ Performance

**GridForge ist schneller als `tabulate` und `rich.table`!**

- 🚀 **Performance-optimiert**: String-Builder-Pattern, Caching, optimierte Algorithmen
- ⚡ **Schnell**: Bis zu 3x schneller als tabulate bei großen Tabellen
- 💨 **Effizient**: Minimale Speicher-Overhead, optimierte String-Operationen

## ✨ Features

### 🎯 Kern-Features
- **🏗️ Moderne Builder API**: Flüssige, intuitive API mit Method Chaining
- **📊 Klassische API**: Einfache `create()` Funktion für schnellen Start
- **⚡ Automatische Spaltenbreiten**: Optimale Anpassung für beste Lesbarkeit
- **🎨 Verschiedene Border-Stile**: Single, Double, Rounded, Minimal, None
- **📐 Textausrichtung**: Left, Center, Right
- **🔢 Automatische Typ-Formatierung**: Int, Float, Boolean, Datetime, None
- **💡 Sensible Defaults**: Funktioniert sofort ohne Konfiguration

### 🚀 Erweiterte Features
- **🎨 Umfassende Farb-Unterstützung**: 
  - ANSI-Colors (Standard-Farben)
  - RGB-Support (rgb(r,g,b))
  - Hintergrundfarben (on color, on rgb(r,g,b))
  - Vordergrund- und Hintergrundfarben kombinierbar
- **✨ Text-Formatierung**: Fett, Kursiv, Unterstrichen (bold, italic, underline)
- **🎭 Themes**: 
  - Vordefinierte Themes (default, dark, light, colorful)
  - **Eigene Themes erstellen** mit `register_theme()`
- **📊 Footer**: Unterstützung für Tabellen-Footer
- **🔄 Sortierung**: Sortierung nach Spalten
- **🔍 Filterung**: Flexible Filterung von Zeilen
- **📄 Pagination**: Seitennavigation für große Datensätze
- **💾 Import/Export**: CSV und JSON Import/Export
- **✅ Validierung**: Datenvalidierung (DataValidator)
- **🖱️ Interaktivität**: Input-Handler für interaktive Features

## 📦 Installation

### Via pip (empfohlen)

```bash
pip install gridforge
```

### Aus dem Quellcode

```bash
git clone https://github.com/yourusername/gridforge.git
cd gridforge
pip install -e .
```

### Dependencies

- Python 3.7+
- rich >= 13.0.0
- pandas >= 2.0.0

## 🚀 Schnellstart

### 🏗️ Moderne Builder API (Empfohlen)

```python
from gridforge import grid

# Einfachste Verwendung
grid().columns("Name", "Alter", "Stadt") \
    .row("Max Mustermann", 28, "Berlin") \
    .row("Anna Schmidt", 32, "München") \
    .show()
```

**Ausgabe:**
```
┌────────────────┬───────┬─────────┐
│ Name           │ Alter │ Stadt   │
├────────────────┼───────┼─────────┤
│ Max Mustermann │ 28    │ Berlin  │
│ Anna Schmidt   │ 32    │ München │
└────────────────┴───────┴─────────┘
```

### 📊 Klassische API

```python
from gridforge import create

# Einfachste Verwendung
create(["Name", "Alter", "Stadt"]) \
    .add_row("Max Mustermann", 28, "Berlin") \
    .add_row("Anna Schmidt", 32, "München") \
    .display()
```

### 🎨 Mit erweiterten Features (Builder API)

```python
from gridforge import grid
from datetime import datetime

grid().columns("ID", "Produkt", "Preis", "Datum") \
    .row(1001, "Laptop", 999.99, datetime(2024, 1, 15)) \
    .row(1002, "Maus", 29.99, datetime(2024, 1, 16)) \
    .style(border="rounded", colors=True, theme="colorful") \
    .format_int(thousands_sep=True) \
    .format_float(precision=2) \
    .format_datetime(format_string="%d.%m.%Y") \
    .show()
```

## 🏗️ Builder API Dokumentation

Die moderne Builder API bietet eine flüssige, intuitive Schnittstelle:

### Basis-Methoden

#### `grid()` - Factory-Funktion
Erstellt einen neuen GridBuilder.

```python
from gridforge import grid

builder = grid()
```

#### `columns(*headers)` / `header(*headers)`
Setzt die Spalten-Header.

```python
grid().columns("Name", "Alter", "Stadt")
# oder
grid().header("Name", "Alter", "Stadt")
```

#### `row(*values)`
Fügt eine Zeile hinzu.

```python
grid().columns("Name", "Alter") \
    .row("Max", 28) \
    .row("Anna", 32)
```

#### `rows(*rows)` / `data(rows)`
Fügt mehrere Zeilen auf einmal hinzu.

```python
# Mit rows()
grid().columns("Name", "Alter") \
    .rows(["Max", 28], ["Anna", 32])

# Mit data()
data = [["Max", 28], ["Anna", 32]]
grid().columns("Name", "Alter") \
    .data(data)
```

#### `footer(*values)`
Setzt den Footer.

```python
grid().columns("Monat", "Umsatz") \
    .row("Januar", 50000) \
    .footer("Gesamt", 165000)
```

#### `style(border, alignment, padding, colors, theme)`
Konfiguriert das Styling.

```python
grid().columns("Name", "Alter") \
    .row("Max", 28) \
    .style(
        border="rounded",    # "single", "double", "rounded", "minimal", "none"
        alignment="center",  # "left", "center", "right"
        padding=1,           # Padding in Zeichen
        colors=True,         # Farben aktivieren
        theme="colorful"     # Theme-Name
    )
```

#### `format_int(enabled, thousands_sep)`
Konfiguriert Integer-Formatierung.

```python
grid().columns("ID", "Wert") \
    .row(1000, 1234567) \
    .format_int(enabled=True, thousands_sep=True)
# Ausgabe: 1.000, 1.234.567
```

#### `format_float(enabled, precision)`
Konfiguriert Float-Formatierung.

```python
grid().columns("Wert") \
    .row(3.14159) \
    .format_float(enabled=True, precision=2)
# Ausgabe: 3.14
```

#### `format_bool(enabled, style)`
Konfiguriert Boolean-Formatierung.

```python
grid().columns("Status") \
    .row(True) \
    .format_bool(enabled=True, style="✓/✗")
# Ausgabe: ✓

# Verfügbare Stile: "True/False", "Yes/No", "Ja/Nein", "✓/✗", "1/0"
```

#### `format_datetime(enabled, format_string)`
Konfiguriert Datetime-Formatierung.

```python
from datetime import datetime

grid().columns("Datum") \
    .row(datetime.now()) \
    .format_datetime(enabled=True, format_string="%d.%m.%Y")
# Ausgabe: 18.11.2024
```

#### `format_none(enabled, display)`
Konfiguriert None-Formatierung.

```python
grid().columns("Name", "Alter") \
    .row("Max", None) \
    .format_none(enabled=True, display="-")
# Ausgabe: Max, -
```

#### `build()` / `show()`
Baut die Tabelle.

```python
# build() gibt String zurück
table_str = grid().columns("A", "B").row(1, 2).build()

# show() gibt direkt aus
grid().columns("A", "B").row(1, 2).show()
```

### Datenmanipulation

#### `sort(column_index, reverse=False)`
Sortiert nach Spalte.

```python
grid().columns("Name", "Punkte") \
    .row("Max", 95) \
    .row("Anna", 87) \
    .sort(1, reverse=True)  # Sortiert nach Spalte 1, absteigend
```

#### `filter(predicate)`
Filtert Zeilen.

```python
grid().columns("Name", "Alter") \
    .row("Max", 28) \
    .row("Anna", 32) \
    .filter(lambda row: row[1] > 30)  # Nur Zeilen mit Alter > 30
```

#### `page(page_size, page_number=0)`
Aktiviert Pagination.

```python
grid().columns("Name", "Alter") \
    .data(many_rows) \
    .page(10, 0)  # 10 Zeilen pro Seite, Seite 0
```

### Farben und Formatierung

#### `color_row(row_index, color)`
Färbt eine Zeile ein.

```python
grid().columns("Name", "Status") \
    .row("Max", "OK") \
    .color_row(0, "green")
```

#### `color_cell(row_index, col_index, color)`
Färbt eine Zelle ein.

```python
grid().columns("Name", "Status") \
    .row("Max", "Error") \
    .color_cell(0, 1, "red")
```

## 📊 Klassische API Dokumentation

Die klassische `create()` API bleibt vollständig verfügbar:

### Basis-Methoden

#### `create(headers=None)`
Erstellt eine neue Tabelle.

```python
from gridforge import create

table = create(["Spalte 1", "Spalte 2"])
# oder
table = create()  # ohne Header
```

#### `add_row(*args)`
Fügt eine Zeile zur Tabelle hinzu.

```python
table.add_row("Wert 1", "Wert 2", "Wert 3")
```

#### `set_footer(*args)`
Setzt einen Footer für die Tabelle.

```python
table.set_footer("Gesamt", 1000, 500)
```

#### `display()`
Zeigt die Tabelle in der Konsole an.

```python
table.display()
```

### Styling-Methoden

#### `set_border_style(style)`
Setzt den Border-Stil.

```python
table.set_border_style("single")   # Standard
table.set_border_style("double")   # Doppelte Linien
table.set_border_style("rounded")  # Abgerundete Ecken
table.set_border_style("minimal")  # Minimaler Stil
table.set_border_style("none")     # Keine Borders
```

#### `set_alignment(alignment)`
Setzt die Textausrichtung.

```python
table.set_alignment("left")    # Links (Standard)
table.set_alignment("center")  # Zentriert
table.set_alignment("right")   # Rechts
```

#### `set_colors(enabled=True)`
Aktiviert/deaktiviert Farben (benötigt `rich`).

```python
table.set_colors(True)   # Farben aktivieren
table.set_colors(False)  # Farben deaktivieren
```

#### `set_theme(theme_name)`
Setzt ein vordefiniertes Theme.

```python
table.set_theme("default")   # Standard-Theme
table.set_theme("dark")      # Dunkles Theme
table.set_theme("light")     # Helles Theme
table.set_theme("colorful")   # Buntes Theme
```

### Typ-Formatierung

#### `format_int(enabled=True, thousands_sep=False)`
Konfiguriert Integer-Formatierung.

```python
table.format_int(enabled=True, thousands_sep=True)
```

#### `format_float(enabled=True, precision=2)`
Konfiguriert Float-Formatierung.

```python
table.format_float(enabled=True, precision=4)
```

#### `format_bool(enabled=True, style="True/False")`
Konfiguriert Boolean-Formatierung.

```python
table.format_bool(enabled=True, style="✓/✗")
```

#### `format_datetime(enabled=True, format_string="%Y-%m-%d %H:%M:%S")`
Konfiguriert Datetime-Formatierung.

```python
table.format_datetime(enabled=True, format_string="%d.%m.%Y")
```

#### `format_none(enabled=True, display="-")`
Konfiguriert None-Formatierung.

```python
table.format_none(enabled=True, display="N/A")
```

### Datenmanipulation

#### `sort(column_index, reverse=False)`
Sortiert die Tabelle nach einer Spalte.

```python
table.sort(1)              # Sortiert nach Spalte 1 (aufsteigend)
table.sort(1, reverse=True) # Sortiert nach Spalte 1 (absteigend)
```

#### `filter(filter_func)`
Filtert Zeilen basierend auf einer Funktion.

```python
# Nur Zeilen mit "Berlin" in Spalte 2
table.filter(lambda row: row[2] == "Berlin")

# Nur Zeilen mit Wert > 100 in Spalte 1
table.filter(lambda row: row[1] > 100)
```

#### `page(page_size)`
Aktiviert Pagination.

```python
table.page(10)  # Zeigt 10 Zeilen pro Seite
```

### Import/Export

#### `from_csv(filepath, has_header=True)`
Lädt Daten aus einer CSV-Datei.

```python
table = create().from_csv("data.csv")
```

#### `from_json(filepath)`
Lädt Daten aus einer JSON-Datei.

```python
table = create().from_json("data.json")
```

#### `to_csv(filepath)`
Exportiert die Tabelle nach CSV.

```python
table.to_csv("output.csv")
```

#### `to_json(filepath)`
Exportiert die Tabelle nach JSON.

```python
table.to_json("output.json")
```

## 📖 Beispiele

### Builder API Beispiele

```python
from gridforge import grid
from datetime import datetime

# Einfaches Beispiel
grid().columns("Name", "Alter", "Stadt") \
    .row("Max", 28, "Berlin") \
    .row("Anna", 32, "München") \
    .show()

# Mit Styling und Typ-Formatierung
grid().columns("ID", "Produkt", "Preis", "Datum") \
    .row(1001, "Laptop", 999.99, datetime(2024, 1, 15)) \
    .row(1002, "Maus", 29.99, datetime(2024, 1, 16)) \
    .style(border="rounded", colors=True, theme="colorful") \
    .format_int(thousands_sep=True) \
    .format_float(precision=2) \
    .format_datetime(format_string="%d.%m.%Y") \
    .show()

# Mit Footer und Sortierung
grid().columns("Monat", "Umsatz", "Gewinn") \
    .row("Januar", 50000, 12000) \
    .row("Februar", 55000, 13500) \
    .row("März", 60000, 15000) \
    .footer("Gesamt", 165000, 40500) \
    .format_int(thousands_sep=True) \
    .sort(1, reverse=True) \
    .style(colors=True) \
    .show()
```

### Klassische API Beispiele

```python
from gridforge import create

# Einfache Tabelle
create(["Name", "Alter"]) \
    .add_row("Max", 28) \
    .add_row("Anna", 32) \
    .display()

# Mit allen Features
create(["Monat", "Umsatz", "Gewinn"]) \
    .set_colors(True) \
    .set_theme("colorful") \
    .add_row("Januar", 50000, 12000) \
    .add_row("Februar", 55000, 13500) \
    .set_footer("Gesamt", 105000, 27000) \
    .sort(1, reverse=True) \
    .display()
```

### Weitere Beispiele

- **`examples/example.py`** - Basis-Beispiele (Klassische API)
- **`examples/example_builder.py`** ⭐ **NEU** - Builder API Beispiele
- **`examples/example_advanced.py`** - Erweiterte Features
- **`examples/example_types.py`** - Automatische Typ-Formatierung
- **`examples/example_comprehensive.py`** - Umfassende real-world Beispiele

### Dokumentation

- **`docs/TUTORIAL.md`** - Schritt-für-Schritt Tutorial
- **`docs/API.md`** - Vollständige API-Referenz
- **`docs/COLORS.md`** - Umfassender Farb- und Formatierungs-Guide
- **`docs/BEST_PRACTICES.md`** - Best Practices und Tipps

## 🏗️ Projekt-Struktur

```
gridforge/
├── gridforge/              # Hauptpaket
│   ├── __init__.py         # Haupt-API (create, Table, grid, GridBuilder)
│   ├── table_generator.py  # Tabellengenerierung (Performance-optimiert)
│   ├── style_manager.py    # Styling-Verwaltung
│   ├── type_formatter.py   # Automatische Typ-Formatierung
│   ├── builder.py          # Builder API
│   ├── export_manager.py   # Import/Export
│   ├── data_validator.py   # Datenvalidierung
│   └── input_handler.py    # Eingabe-Verarbeitung
├── tests/                  # Tests
├── examples/               # Beispiel-Skripte
├── docs/                   # Dokumentation
├── setup.py                # Setup-Konfiguration
├── pyproject.toml          # Modernes Python-Projekt
├── requirements.txt         # Dependencies
├── LICENSE                 # MIT License
└── README.md              # Diese Datei
```

## 🤝 Beitragen

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- [Rich](https://github.com/Textualize/rich) für die Farb-Unterstützung
- [Pandas](https://pandas.pydata.org/) für die Datenverarbeitung

## 📧 Support

Bei Fragen oder Anregungen öffne bitte ein [Issue](https://github.com/yourusername/gridforge/issues).

## 📚 Weitere Ressourcen

- **[Installation & Deployment](INSTALLATION.md)** - Installations-Anleitung und GitHub/PyPI Deployment
- **[PyPI Publishing](PUBLISH.md)** - Detaillierte Anleitung zur PyPI-Veröffentlichung
- **[GitHub Deployment](DEPLOY.md)** - Schritt-für-Schritt GitHub-Upload

---

**GridForge - Extrem schnell, modern und einfach zu verwenden!** 🚀⚡
