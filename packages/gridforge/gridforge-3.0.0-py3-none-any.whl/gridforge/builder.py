"""
GridBuilder - Moderne, flüssige Table-Builder API für GridForge.
"""

from typing import List, Any, Optional, Callable
from .table_generator import TableGenerator
from .style_manager import StyleManager
from .type_formatter import TypeFormatter


class GridBuilder:
    """
    Moderne, flüssige Builder-API für Tabellen.
    
    Beispiel:
        grid = GridBuilder()
        grid.columns("Name", "Alter", "Stadt") \
            .row("Max", 28, "Berlin") \
            .row("Anna", 32, "München") \
            .style(border="rounded", colors=True) \
            .format_int(thousands_sep=True) \
            .build()
    """
    
    def __init__(self):
        self._headers: List[str] = []
        self._rows: List[List[Any]] = []
        self._footer: Optional[List[Any]] = None
        self._generator = TableGenerator()
        self._style_manager = StyleManager()
        self._type_formatter = TypeFormatter()
        self._built = False
    
    def columns(self, *headers: str) -> 'GridBuilder':
        """
        Setzt die Spalten-Header.
        
        Args:
            *headers: Spalten-Header als separate Argumente
        
        Returns:
            self für Method-Chaining
        """
        self._headers = list(headers)
        return self
    
    def header(self, *headers: str) -> 'GridBuilder':
        """Alias für columns()."""
        return self.columns(*headers)
    
    def row(self, *values: Any) -> 'GridBuilder':
        """
        Fügt eine Zeile hinzu.
        
        Args:
            *values: Zellwerte als separate Argumente
        
        Returns:
            self für Method-Chaining
        """
        self._rows.append(list(values))
        return self
    
    def rows(self, *rows: List[Any]) -> 'GridBuilder':
        """
        Fügt mehrere Zeilen hinzu.
        
        Args:
            *rows: Listen von Zeilen
        
        Returns:
            self für Method-Chaining
        """
        for row in rows:
            self._rows.append(list(row) if isinstance(row, (list, tuple)) else [row])
        return self
    
    def data(self, rows: List[List[Any]]) -> 'GridBuilder':
        """
        Setzt alle Zeilen auf einmal.
        
        Args:
            rows: Liste von Zeilen (jede Zeile ist eine Liste von Werten)
        
        Returns:
            self für Method-Chaining
        """
        self._rows = [list(row) for row in rows]
        return self
    
    def footer(self, *values: Any) -> 'GridBuilder':
        """
        Setzt den Footer.
        
        Args:
            *values: Footer-Werte als separate Argumente
        
        Returns:
            self für Method-Chaining
        """
        self._footer = list(values)
        return self
    
    def style(self, 
              border: str = "single",
              alignment: str = "left",
              padding: int = 1,
              colors: bool = False,
              theme: Optional[str] = None) -> 'GridBuilder':
        """
        Konfiguriert das Styling.
        
        Args:
            border: Border-Stil ("single", "double", "rounded", "minimal", "none")
            alignment: Textausrichtung ("left", "center", "right")
            padding: Padding in Zeichen
            colors: Aktiviert Farben
            theme: Theme-Name (optional)
        
        Returns:
            self für Method-Chaining
        """
        self._style_manager.set_border_style(border)
        self._style_manager.set_alignment(alignment)
        self._style_manager.set_padding(padding)
        self._style_manager.set_colors(colors)
        if theme:
            self._style_manager.set_theme(theme)
        return self
    
    def format_int(self, enabled: bool = True, thousands_sep: bool = False) -> 'GridBuilder':
        """Konfiguriert Integer-Formatierung."""
        self._type_formatter.set_int_formatting(enabled, thousands_sep)
        return self
    
    def format_float(self, enabled: bool = True, precision: int = 2) -> 'GridBuilder':
        """Konfiguriert Float-Formatierung."""
        self._type_formatter.set_float_formatting(enabled, precision)
        return self
    
    def format_bool(self, enabled: bool = True, style: str = "True/False") -> 'GridBuilder':
        """Konfiguriert Boolean-Formatierung."""
        self._type_formatter.set_bool_formatting(enabled, style)
        return self
    
    def format_datetime(self, enabled: bool = True, format_string: str = "%Y-%m-%d %H:%M:%S") -> 'GridBuilder':
        """Konfiguriert Datetime-Formatierung."""
        self._type_formatter.set_datetime_formatting(enabled, format_string)
        return self
    
    def format_none(self, enabled: bool = True, display: str = "-") -> 'GridBuilder':
        """Konfiguriert None-Formatierung."""
        self._type_formatter.set_none_formatting(enabled, display)
        return self
    
    def color_row(self, row_index: int, color: str) -> 'GridBuilder':
        """Färbt eine Zeile ein."""
        self._style_manager.set_row_color(row_index, color)
        return self
    
    def color_cell(self, row_index: int, col_index: int, color: str) -> 'GridBuilder':
        """Färbt eine Zelle ein."""
        self._style_manager.set_cell_color(row_index, col_index, color)
        return self
    
    def sort(self, column_index: int, reverse: bool = False) -> 'GridBuilder':
        """Sortiert nach Spalte."""
        self._generator.sort(column_index, reverse)
        return self
    
    def filter(self, predicate: Callable[[List[Any]], bool]) -> 'GridBuilder':
        """Filtert Zeilen."""
        self._generator.filter(predicate)
        return self
    
    def page(self, page_size: int, page_number: int = 0) -> 'GridBuilder':
        """Aktiviert Pagination."""
        self._generator.set_page_size(page_size)
        self._generator.set_page(page_number)
        return self
    
    def build(self) -> str:
        """
        Baut die Tabelle und gibt den formatierten String zurück.
        
        Returns:
            Formatierter Tabellen-String
        """
        if self._built:
            # Wenn bereits gebaut, nur neu generieren
            return self._generator.generate()
        
        # Setze Daten
        self._generator.set_data(self._headers, self._rows, self._footer)
        self._generator.set_style_manager(self._style_manager)
        self._built = True
        
        return self._generator.generate()
    
    def show(self) -> 'GridBuilder':
        """
        Baut und zeigt die Tabelle an.
        
        Returns:
            self für Method-Chaining
        """
        output = self.build()
        
        # Rich-Formatierung ausgeben (falls verfügbar)
        if self._style_manager._use_colors and self._style_manager._console:
            self._style_manager._console.print(output)
        else:
            print(output)
        
        return self
    
    def __str__(self) -> str:
        """Gibt die formatierte Tabelle zurück."""
        return self.build()
    
    def __repr__(self) -> str:
        """Gibt eine Repräsentation zurück."""
        return f"GridBuilder(columns={len(self._headers)}, rows={len(self._rows)})"


def grid() -> GridBuilder:
    """
    Factory-Funktion zum Erstellen eines neuen GridBuilder.
    
    Returns:
        Neuer GridBuilder
    """
    return GridBuilder()

