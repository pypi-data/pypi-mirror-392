from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def seteffect_typewriter(interpreter: "ConslyricInterpreter", speed: str):
    """Applies typewriter effect."""
    interpreter.current_effect = {
        "type": "typewriter",
        "speed": interpreter._parse_time_string(speed),
    }
    interpreter.logger.debug(f"Typewriter effect set with speed {speed}")
