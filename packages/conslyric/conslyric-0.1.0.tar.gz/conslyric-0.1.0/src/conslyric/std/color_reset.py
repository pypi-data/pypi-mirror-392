from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def color_reset(interpreter: "ConslyricInterpreter"):
    """Resets the text color to default."""
    interpreter.current_text_color = None
    interpreter.logger.debug("Text color reset.")
