from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter

def enditer(interpreter: "ConslyricInterpreter"):
    """Enter the iterater."""
    interpreter.iter = False
    interpreter.iter_count = None
    interpreter.logger.debug("Exited from iterator")
