"""
Configuration settings for Vuno editor.
"""

class Config:
    """Editor configuration."""

    def __init__(self):
        # Display settings
        self.show_line_numbers = False
        self.tab_width = 4
        self.wrap_lines = False
        self.show_scrollbar = True

        # Editor behavior
        self.auto_indent = True
        self.trim_trailing_whitespace = False
        self.insert_spaces_for_tabs = True

        # UI settings
        self.show_status_bar = True
        self.show_help_bar = True
        self.show_message_bar = True

        # Search settings
        self.case_sensitive_search = False
        self.wrap_search = True

        # Undo settings
        self.max_undo_levels = 100

        # File settings
        self.default_encoding = 'utf-8'
        self.backup_files = False

    def toggle_line_numbers(self):
        """Toggle line numbers on/off."""
        self.show_line_numbers = not self.show_line_numbers
        return self.show_line_numbers