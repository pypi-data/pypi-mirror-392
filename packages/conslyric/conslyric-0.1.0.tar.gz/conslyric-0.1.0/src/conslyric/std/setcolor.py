from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def setcolor(interpreter: "ConslyricInterpreter", color: str):
    """Sets the text color."""
    interpreter.current_text_color = color
    interpreter.logger.debug(f"[dim]Text color set to {color}[/dim]")
