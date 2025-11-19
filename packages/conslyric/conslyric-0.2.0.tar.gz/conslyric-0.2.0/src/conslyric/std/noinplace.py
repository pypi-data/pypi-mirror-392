from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def noinplace(interpreter: "ConslyricInterpreter"):
    """Disables in-place (overwrite) mode."""
    interpreter.inplace_mode = False
    interpreter.logger.debug("In-place mode disabled.")
