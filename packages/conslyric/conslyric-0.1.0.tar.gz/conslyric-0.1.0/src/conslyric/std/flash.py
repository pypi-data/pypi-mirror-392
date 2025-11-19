import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def flash(interpreter: "ConslyricInterpreter", color: str, duration: str):
    """Flashes the screen with a given color."""
    flash_duration = interpreter._parse_time_string(duration)
    original_color = interpreter.current_text_color
    interpreter.console.print(
        " " * interpreter.console.width * interpreter.console.height,
        end="\r",
        overflow="crop", 
        style=f"on {color}"
    )
    time.sleep(flash_duration)
    interpreter.console.clear()
    if original_color:
        interpreter.current_text_color = original_color
    interpreter.logger.debug(f"Flashed screen with {color} for {duration}")
