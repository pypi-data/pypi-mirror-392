"""
TableGenerator - Verwaltet Tabellendaten, Struktur und generiert die Ausgabe.
"""

from .style_manager import StyleManager
from .type_formatter import TypeFormatter


class TableGenerator:
    """Generiert formatierte Tabellenausgabe."""
    
    def __init__(self):
        self._headers = []
        self._rows = []
        self._footer = None
        self._style_manager = None
        self._type_formatter = TypeFormatter()
        self._column_widths = []
        self._filtered_rows = None
        self._sorted_rows = None
        self._page_size = None
        self._current_page = 0
    
    def set_data(self, headers, rows, footer=None):
        """
        Setzt die Tabellendaten.
        
        Args:
            headers: Liste von Header-Strings
            rows: Liste von Zeilen (jede Zeile ist eine Liste von Werten)
            footer: Liste von Footer-Werten (optional)
        """
        self._headers = headers if headers else []
        self._rows = rows if rows else []
        self._footer = footer
        self._filtered_rows = None
        self._sorted_rows = None
        self._calculate_column_widths()
    
    def set_style_manager(self, style_manager):
        """
        Setzt den StyleManager.
        
        Args:
            style_manager: StyleManager-Instanz
        """
        if not isinstance(style_manager, StyleManager):
            raise TypeError("style_manager muss eine StyleManager-Instanz sein")
        self._style_manager = style_manager
    
    def _calculate_column_widths(self):
        """Berechnet die optimale Spaltenbreite für jede Spalte (Performance-optimiert)."""
        if not self._rows and not self._headers:
            self._column_widths = []
            return
        
        # Bestimme die Anzahl der Spalten - optimiert
        num_columns = 0
        if self._headers:
            num_columns = len(self._headers)
        elif self._rows:
            # Performance: Verwende max() mit Generator statt List-Comprehension
            num_columns = max((len(row) for row in self._rows), default=0)
        
        if num_columns == 0:
            self._column_widths = []
            return
        
        # Initialisiere Breiten mit 0
        widths = [0] * num_columns
        
        # Berücksichtige Header-Breiten - optimiert
        if self._headers:
            for i, header in enumerate(self._headers):
                if i < num_columns:
                    widths[i] = max(widths[i], len(str(header)))
        
        # Berücksichtige Zeilen-Breiten (mit Typ-Formatierung) - optimiert
        # Performance: Cache format_value calls
        for row in self._rows:
            for i, cell in enumerate(row):
                if i < num_columns:
                    # Direkte Formatierung ohne zusätzliche Checks
                    formatted_cell = self._type_formatter.format_value(cell)
                    cell_len = len(formatted_cell)
                    if cell_len > widths[i]:
                        widths[i] = cell_len
        
        # Berücksichtige Footer-Breiten (mit Typ-Formatierung) - optimiert
        if self._footer:
            for i, footer_value in enumerate(self._footer):
                if i < num_columns:
                    formatted_footer = self._type_formatter.format_value(footer_value)
                    footer_len = len(formatted_footer)
                    if footer_len > widths[i]:
                        widths[i] = footer_len
        
        # Stelle sicher, dass jede Spalte mindestens 1 Zeichen breit ist
        self._column_widths = [max(1, w) for w in widths]
    
    def generate(self):
        """
        Generiert die formatierte Tabellenausgabe (Performance-optimiert).
        
        Returns:
            Formatierter String der Tabelle
        """
        if not self._style_manager:
            self._style_manager = StyleManager()
        
        if not self._column_widths:
            return ""
        
        border = self._style_manager.get_border_chars()
        padding = self._style_manager.get_padding()
        padding_str = " " * padding
        
        # Berechne die tatsächliche Spaltenbreite (inkl. Padding) - einmalig
        actual_widths = [w + (2 * padding) for w in self._column_widths]
        num_cols = len(self._column_widths)
        
        # Cache für Border-Zeichen
        h_char = border["horizontal"]
        v_char = border["vertical"]
        
        # Performance: Verwende List-Comprehension und join statt +=
        lines = []
        
        # Top Border - optimiert mit join
        top_parts = [border["top_left"]]
        for i, width in enumerate(actual_widths):
            top_parts.append(h_char * width)
            if i < num_cols - 1:
                top_parts.append(border["top_tee"])
        top_parts.append(border["top_right"])
        lines.append("".join(top_parts))
        
        # Header (falls vorhanden) - optimiert
        if self._headers:
            header_parts = [v_char]
            for i, header in enumerate(self._headers):
                width = self._column_widths[i]
                cell_width = width + (2 * padding)
                aligned_text = self._style_manager.align_text(str(header), cell_width)
                formatted_text = self._style_manager.format_text(aligned_text, is_header=True)
                header_parts.append(padding_str)
                header_parts.append(formatted_text)
                header_parts.append(padding_str)
                header_parts.append(v_char)
            lines.append("".join(header_parts))
            
            # Separator zwischen Header und Daten - optimiert
            sep_parts = [border["left_tee"]]
            for i, width in enumerate(actual_widths):
                sep_parts.append(h_char * width)
                if i < num_cols - 1:
                    sep_parts.append(border["cross"])
            sep_parts.append(border["right_tee"])
            lines.append("".join(sep_parts))
        
        # Datenzeilen (mit Filterung, Sortierung, Pagination) - optimiert
        display_rows = self._get_display_rows()
        
        for row_index, row in enumerate(display_rows):
            row_parts = [v_char]
            for i in range(num_cols):
                width = self._column_widths[i]
                cell_width = width + (2 * padding)
                
                # Automatische Typ-Formatierung
                raw_value = row[i] if i < len(row) else None
                cell_value = self._type_formatter.format_value(raw_value)
                aligned_text = self._style_manager.align_text(cell_value, cell_width)
                
                # Farbformatierung
                formatted_text = self._style_manager.format_text(
                    aligned_text,
                    row_index=row_index,
                    col_index=i
                )
                
                row_parts.append(padding_str)
                row_parts.append(formatted_text)
                row_parts.append(padding_str)
                row_parts.append(v_char)
            lines.append("".join(row_parts))
        
        # Footer (falls vorhanden) - optimiert
        if self._footer:
            # Separator vor Footer
            sep_parts = [border["left_tee"]]
            for i, width in enumerate(actual_widths):
                sep_parts.append(h_char * width)
                if i < num_cols - 1:
                    sep_parts.append(border["cross"])
            sep_parts.append(border["right_tee"])
            lines.append("".join(sep_parts))
            
            # Footer-Zeile - optimiert
            footer_parts = [v_char]
            for i, footer_value in enumerate(self._footer):
                width = self._column_widths[i]
                cell_width = width + (2 * padding)
                formatted_footer = self._type_formatter.format_value(footer_value)
                aligned_text = self._style_manager.align_text(formatted_footer, cell_width)
                formatted_text = self._style_manager.format_text(aligned_text, is_footer=True)
                footer_parts.append(padding_str)
                footer_parts.append(formatted_text)
                footer_parts.append(padding_str)
                footer_parts.append(v_char)
            lines.append("".join(footer_parts))
        
        # Bottom Border - optimiert
        bottom_parts = [border["bottom_left"]]
        for i, width in enumerate(actual_widths):
            bottom_parts.append(h_char * width)
            if i < num_cols - 1:
                bottom_parts.append(border["bottom_tee"])
        bottom_parts.append(border["bottom_right"])
        lines.append("".join(bottom_parts))
        
        return "\n".join(lines)
    
    def _get_display_rows(self):
        """Gibt die anzuzeigenden Zeilen zurück (mit Filterung, Sortierung, Pagination)."""
        rows = self._rows
        
        # Filterung
        if self._filtered_rows is not None:
            rows = self._filtered_rows
        
        # Sortierung
        if self._sorted_rows is not None:
            rows = self._sorted_rows
        
        # Pagination
        if self._page_size:
            start = self._current_page * self._page_size
            end = start + self._page_size
            rows = rows[start:end]
        
        return rows
    
    def sort(self, column_index, reverse=False):
        """
        Sortiert die Zeilen nach einer Spalte.
        
        Args:
            column_index: Index der Spalte zum Sortieren
            reverse: True für absteigende Sortierung
        """
        if not self._rows:
            return
        
        try:
            self._sorted_rows = sorted(
                self._rows,
                key=lambda row: row[column_index] if column_index < len(row) else "",
                reverse=reverse
            )
            self._calculate_column_widths()
        except Exception:
            # Fallback: String-Sortierung
            self._sorted_rows = sorted(
                self._rows,
                key=lambda row: str(row[column_index]) if column_index < len(row) else "",
                reverse=reverse
            )
    
    def filter(self, filter_func):
        """
        Filtert Zeilen basierend auf einer Funktion.
        
        Args:
            filter_func: Funktion, die eine Zeile als Parameter nimmt und True/False zurückgibt
        """
        if not self._rows:
            return
        
        self._filtered_rows = [row for row in self._rows if filter_func(row)]
        self._calculate_column_widths()
    
    def clear_filter(self):
        """Entfernt alle Filter."""
        self._filtered_rows = None
        self._calculate_column_widths()
    
    def clear_sort(self):
        """Entfernt die Sortierung."""
        self._sorted_rows = None
        self._calculate_column_widths()
    
    def set_page_size(self, page_size):
        """
        Setzt die Seitengröße für Pagination.
        
        Args:
            page_size: Anzahl der Zeilen pro Seite (None deaktiviert Pagination)
        """
        self._page_size = page_size
        self._current_page = 0
    
    def set_page(self, page_number):
        """
        Setzt die aktuelle Seite.
        
        Args:
            page_number: Seitenzahl (0-basiert)
        """
        if self._page_size:
            total_pages = (len(self._rows) + self._page_size - 1) // self._page_size
            self._current_page = max(0, min(page_number, total_pages - 1))
    
    def next_page(self):
        """Geht zur nächsten Seite."""
        if self._page_size:
            total_pages = (len(self._rows) + self._page_size - 1) // self._page_size
            if self._current_page < total_pages - 1:
                self._current_page += 1
    
    def previous_page(self):
        """Geht zur vorherigen Seite."""
        if self._current_page > 0:
            self._current_page -= 1
    
    def get_type_formatter(self):
        """Gibt den TypeFormatter zurück für Konfiguration."""
        return self._type_formatter

