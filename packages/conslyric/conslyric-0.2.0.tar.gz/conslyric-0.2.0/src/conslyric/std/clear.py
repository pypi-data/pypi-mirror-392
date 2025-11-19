from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def clear(interpreter: "ConslyricInterpreter"):
    """Clears the console screen."""
    interpreter.console.clear()
    interpreter.logger.debug("Console cleared.")
