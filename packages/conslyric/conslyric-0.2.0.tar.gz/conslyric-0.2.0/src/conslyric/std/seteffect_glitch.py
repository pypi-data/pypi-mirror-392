from typing import TYPE_CHECKING

from ..exceptions import ConslyricRuntimeError

if TYPE_CHECKING:
    from ..interpreter import ConslyricInterpreter


def seteffect_glitch(interpreter: "ConslyricInterpreter", intensity: int):
    """Applies glitch effect."""
    if not 1 <= intensity <= 10:
        raise ConslyricRuntimeError(
            "Glitch intensity must be between 1 and 10."
        )
    interpreter.current_effect = {"type": "glitch", "intensity": intensity}
    interpreter.logger.debug(
        f"Glitch effect set with intensity {intensity}"
    )
