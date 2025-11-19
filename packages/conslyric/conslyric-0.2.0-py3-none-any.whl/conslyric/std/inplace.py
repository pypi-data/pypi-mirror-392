from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def inplace(interpreter: "ConslyricInterpreter"):
    """Enables in-place (overwrite) mode."""
    interpreter.inplace_mode = True
    interpreter.logger.debug("In-place mode enabled.")
