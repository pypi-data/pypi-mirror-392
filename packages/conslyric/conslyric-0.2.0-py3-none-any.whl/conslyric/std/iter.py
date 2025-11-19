from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def iter(interpreter: "ConslyricInterpreter", count: int, sleep: Optional[str] = None):
    """Enter the iterater."""
    flash_duration = interpreter._parse_time_string(sleep if sleep else "")

    interpreter.iter = True
    interpreter.iter_count = count
    interpreter.iter_sleep = flash_duration
    interpreter.logger.debug(f"Entered to iterator (count: {count})")
