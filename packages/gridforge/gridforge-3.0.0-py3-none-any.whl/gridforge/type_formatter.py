"""
TypeFormatter - Automatische Typ-Formatierung für verschiedene Datentypen.
"""

from datetime import datetime, date
from typing import Any, Optional


class TypeFormatter:
    """Formatiert verschiedene Datentypen automatisch für die Tabellenanzeige."""
    
    def __init__(self):
        self._format_int = True
        self._format_float = True
        self._format_bool = True
        self._format_datetime = True
        self._format_none = True
        self._int_thousands_sep = False
        self._float_precision = 2
        self._bool_style = "True/False"  # "True/False", "Yes/No", "✓/✗", "1/0"
        self._datetime_format = "%Y-%m-%d %H:%M:%S"
        self._none_display = "-"
    
    def format_value(self, value: Any) -> str:
        """
        Formatiert einen Wert basierend auf seinem Typ.
        
        Args:
            value: Der zu formatierende Wert
        
        Returns:
            Formatierter String
        """
        if value is None:
            return self._format_none_value()
        
        # Datetime
        if isinstance(value, (datetime, date)):
            return self._format_datetime_value(value)
        
        # Boolean
        if isinstance(value, bool):
            return self._format_bool_value(value)
        
        # Integer
        if isinstance(value, int):
            return self._format_int_value(value)
        
        # Float
        if isinstance(value, float):
            return self._format_float_value(value)
        
        # String oder andere Typen
        return str(value)
    
    def _format_none_value(self) -> str:
        """Formatiert None-Werte."""
        if not self._format_none:
            return ""
        return self._none_display
    
    def _format_bool_value(self, value: bool) -> str:
        """Formatiert Boolean-Werte."""
        if not self._format_bool:
            return str(value)
        
        if self._bool_style == "True/False":
            return "True" if value else "False"
        elif self._bool_style == "Yes/No":
            return "Yes" if value else "No"
        elif self._bool_style == "Ja/Nein":
            return "Ja" if value else "Nein"
        elif self._bool_style == "✓/✗":
            return "✓" if value else "✗"
        elif self._bool_style == "1/0":
            return "1" if value else "0"
        elif self._bool_style == "✓/✗":
            return "✓" if value else "✗"
        else:
            return str(value)
    
    def _format_int_value(self, value: int) -> str:
        """Formatiert Integer-Werte."""
        if not self._format_int:
            return str(value)
        
        if self._int_thousands_sep:
            return f"{value:,}".replace(",", ".")
        return str(value)
    
    def _format_float_value(self, value: float) -> str:
        """Formatiert Float-Werte."""
        if not self._format_float:
            return str(value)
        
        # Runde auf gewünschte Präzision
        rounded = round(value, self._float_precision)
        
        # Entferne unnötige .0 bei ganzen Zahlen
        if rounded == int(rounded):
            return str(int(rounded))
        
        # Formatiere mit f-String
        return f"{rounded:.{self._float_precision}f}"
    
    def _format_datetime_value(self, value: datetime | date) -> str:
        """Formatiert Datetime/Date-Werte."""
        if not self._format_datetime:
            return str(value)
        
        if isinstance(value, datetime):
            return value.strftime(self._datetime_format)
        elif isinstance(value, date):
            # Für date-Objekte nur Datum formatieren
            return value.strftime(self._datetime_format.split()[0] if " " in self._datetime_format else self._datetime_format)
        
        return str(value)
    
    def set_int_formatting(self, enabled: bool = True, thousands_sep: bool = False):
        """
        Konfiguriert Integer-Formatierung.
        
        Args:
            enabled: Aktiviert/deaktiviert Integer-Formatierung
            thousands_sep: Aktiviert Tausendertrennzeichen
        """
        self._format_int = enabled
        self._int_thousands_sep = thousands_sep
    
    def set_float_formatting(self, enabled: bool = True, precision: int = 2):
        """
        Konfiguriert Float-Formatierung.
        
        Args:
            enabled: Aktiviert/deaktiviert Float-Formatierung
            precision: Anzahl der Dezimalstellen
        """
        self._format_float = enabled
        self._float_precision = max(0, min(precision, 10))  # 0-10 Dezimalstellen
    
    def set_bool_formatting(self, enabled: bool = True, style: str = "True/False"):
        """
        Konfiguriert Boolean-Formatierung.
        
        Args:
            enabled: Aktiviert/deaktiviert Boolean-Formatierung
            style: Stil ("True/False", "Yes/No", "Ja/Nein", "✓/✗", "1/0")
        """
        self._format_bool = enabled
        valid_styles = ["True/False", "Yes/No", "Ja/Nein", "✓/✗", "1/0"]
        if style in valid_styles:
            self._bool_style = style
    
    def set_datetime_formatting(self, enabled: bool = True, format_string: str = "%Y-%m-%d %H:%M:%S"):
        """
        Konfiguriert Datetime-Formatierung.
        
        Args:
            enabled: Aktiviert/deaktiviert Datetime-Formatierung
            format_string: strftime-Format-String
        """
        self._format_datetime = enabled
        self._datetime_format = format_string
    
    def set_none_formatting(self, enabled: bool = True, display: str = "-"):
        """
        Konfiguriert None-Formatierung.
        
        Args:
            enabled: Aktiviert/deaktiviert None-Formatierung
            display: Anzuzeigender Text für None (z.B. "-", "N/A", "")
        """
        self._format_none = enabled
        self._none_display = display

