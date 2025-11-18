import json
from termcolor import colored
from typing import Any, Optional

class ColoryPPrint:
    """
    ColoryPPrint for color-coded JSON logging with customizable end character.

    Available foreground colors:
        black, red, green, yellow, blue, magenta, cyan, white,
        grey, light_red, light_green, light_yellow, light_blue,
        light_magenta, light_cyan, light_white.

    Available background colors (prefix with "on_"):
        on_black, on_red, on_green, on_yellow, on_blue, on_magenta,
        on_cyan, on_white, on_grey, on_light_red, on_light_green,
        on_light_yellow, on_light_blue, on_light_magenta,
        on_light_cyan, on_light_white.

    Available text styles:
        bold, underline, reverse, concealed.

    Example usage:
        log.red.bold({"status": "error", "message": "An error occurred!"}, end=" ")
        log.green.on_black.underline({"status": "success", "message": "Operation successful."})
        log({"message": "Default logging with cyan."}, end="")
    """

    def __init__(self, debug: bool = False):
        self.fg = 'cyan'  # Default foreground color
        self.bg = None    # Default background color
        self.attrs = []   # Default styles
        self.end = "\n"   # Default end character
        self.debug = debug

    def _reset(self):
        """Reset styles and end to defaults after logging."""
        self.fg = 'cyan'
        self.bg = None
        self.attrs = []
        self.end = "\n"

    def _apply_formatting(self, text: str) -> str:
        """Apply formatting based on current styles."""
        return colored(text, self.fg, self.bg, attrs=self.attrs)

    def _log(self, data: Any, force: bool, end: Optional[str]):
        """Dump data as JSON, apply formatting, and print with custom end."""
        def custom_serializer(obj: Any) -> str:
            """Handle non-serializable objects by returning their `repr`."""
            try:
                return json.JSONEncoder().default(obj)
            except TypeError:
                # Use the `repr()` for non-serializable objects
                return f"<{type(obj).__name__} object at {hex(id(obj))}>"
        
        json_data = json.dumps(data, default=custom_serializer, indent=3, ensure_ascii=False)
        if self.debug or force:
            print(self._apply_formatting(json_data), end=end)
        self._reset()

    def __call__(self, data: Any, force: bool = False, end: Optional[str] = "\n"):
        """Allow direct logging by calling the log object with optional end."""
        self.end = end  # Temporarily store for this call
        self._log(data, force, end)
    
    def __getattr__(self, name: str) -> "ColoryPPrint":
        """
        Dynamically handle chaining of colors, backgrounds, and styles.

        Raises:
            AttributeError: If the attribute is invalid.
        """
        colors = {
            "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
            "grey", "light_red", "light_green", "light_yellow", "light_blue",
            "light_magenta", "light_cyan", "light_white"
        }
        backgrounds = {f"on_{color}" for color in colors}
        styles = {"bold", "underline", "reverse", "concealed"}

        if name in colors:
            self.fg = name
            return self
        elif name in backgrounds:
            self.bg = name
            return self
        elif name in styles:
            self.attrs.append(name)
            return self
        else:
            raise AttributeError(f"'ColoryPPrint' object has no attribute '{name}'")