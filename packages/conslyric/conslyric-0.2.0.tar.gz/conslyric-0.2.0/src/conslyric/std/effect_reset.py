from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def effect_reset(interpreter: "ConslyricInterpreter"):
    """Resets all visual effects."""
    interpreter.current_effect = None
    interpreter.logger.debug("Visual effects reset.")
