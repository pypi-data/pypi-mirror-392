import logging
import random
import re
import time
from typing import Any, Dict, Optional

from rich.console import Console
from rich.text import Text

from .exceptions import ConslyricRuntimeError
from .std import (
    clear,
    color_reset,
    effect_reset,
    flash,
    inplace,
    noinplace,
    setcolor,
    seteffect_glitch,
    seteffect_typewriter,
)


class ConslyricInterpreter:
    """
    Interprets Conslyric data and executes commands.
    """

    def __init__(self, conslyric_data: Dict[str, Any]):
        self.logger = logging.getLogger("conslyric.interpreter")
        self.data = conslyric_data
        self.console = Console()
        self.current_show_duration = self._parse_time_string(
            self.data["metadata"]["showDefault"]
        )
        self.current_sleep_duration = self._parse_time_string(
            self.data["metadata"]["sleepDefault"]
        )
        self.total_elapsed_time = 0.0
        self.time_limit = self._parse_time_string(self.data["metadata"]["time"])
        self.inplace_mode = False
        self.current_text_color: Optional[str] = (
            None  # rich color string or None
        )
        self.current_effect: Optional[dict] = (
            None  # e.g., {'type': 'typewriter', 'speed': 0.1}
        )

        # Placeholder for defined functions
        self.defined_functions = self.data.get("define", {})

        # Register standard library commands
        self.std_commands = {
            "cons:clear": clear,
            "cons:setcolor": setcolor,
            "cons:color:reset": color_reset,
            "cons:flash": flash,
            "cons:seteffect:typewriter": seteffect_typewriter,
            "cons:seteffect:glitch": seteffect_glitch,
            "cons:effect:reset": effect_reset,
            "cons:inplace": inplace,
            "cons:noinplace": noinplace,
        }

    def _parse_time_string(self, time_str: str) -> float:
        """Parses time strings like '2s', '500ms' into seconds (float)."""
        if time_str.endswith("s"):
            return float(time_str[:-1])
        elif time_str.endswith("ms"):
            return float(time_str[:-2]) / 1000
        else:
            raise ValueError(f"Invalid time format: {time_str}")

    def _pre_calculate_command_time(
        self,
        command_name: str,
        args: Dict[str, Any],
        current_state: Dict[str, Any],
    ) -> float:
        """
        Simulates command execution to calculate time and update state for pre-calculation.
        Returns the time consumed by the command itself (e.g., flash duration).
        Updates current_state in place for rules and effects.
        """
        time_consumed = 0.0
        cmd_without_prefix = command_name[2:]

        if command_name.startswith("::cons:"):
            # Standard library commands
            if cmd_without_prefix == "cons:setcolor":
                current_state["current_text_color"] = args.get("color")
            elif cmd_without_prefix == "cons:color:reset":
                current_state["current_text_color"] = None
            elif cmd_without_prefix == "cons:flash":
                duration_str = args.get("duration")
                if duration_str:
                    time_consumed = self._parse_time_string(duration_str)
            elif cmd_without_prefix == "cons:seteffect:typewriter":
                speed = args.get("speed")
                if speed is None:
                    raise ConslyricRuntimeError(
                        "::cons:seteffect:typewriter requires 'speed' argument."
                    )
                current_state["current_effect"] = {
                    "type": "typewriter",
                    "speed": self._parse_time_string(speed),
                }
            elif cmd_without_prefix == "cons:seteffect:glitch":
                intensity = args.get("intensity")
                if intensity is None:
                    raise ConslyricRuntimeError(
                        "::cons:seteffect:glitch requires 'intensity' argument."
                    )
                current_state["current_effect"] = {
                    "type": "glitch",
                    "intensity": intensity,
                }
            elif cmd_without_prefix == "cons:effect:reset":
                current_state["current_effect"] = None
            elif cmd_without_prefix == "cons:inplace":
                current_state["inplace_mode"] = True
            elif cmd_without_prefix == "cons:noinplace":
                current_state["inplace_mode"] = False
            elif cmd_without_prefix == "cons:clear":
                pass
            else:
                self.logger.warning(
                    f"Unknown standard command during pre-calculation: {command_name}"
                )
        elif command_name.startswith("::"):
            # Custom commands or internal commands
            if cmd_without_prefix == "setShowRule":
                duration_str = args.get("duration")
                if not duration_str:
                    raise ConslyricRuntimeError(
                        "::setShowRule requires 'duration' argument."
                    )
                current_state["current_show_duration"] = (
                    self._parse_time_string(duration_str)
                )
            elif cmd_without_prefix == "setSleepRule":
                duration_str = args.get("duration")
                if not duration_str:
                    raise ConslyricRuntimeError(
                        "::setSleepRule requires 'duration' argument."
                    )
                current_state["current_sleep_duration"] = (
                    self._parse_time_string(duration_str)
                )
            elif cmd_without_prefix == "endSection":
                current_state["current_show_duration"] = (
                    self._parse_time_string(
                        self.data["metadata"]["showDefault"]
                    )
                )
                current_state["current_sleep_duration"] = (
                    self._parse_time_string(
                        self.data["metadata"]["sleepDefault"]
                    )
                )
            elif cmd_without_prefix in self.defined_functions:
                func_def = self.defined_functions[cmd_without_prefix]
                if func_def.get("type") != "func":
                    raise ConslyricRuntimeError(
                        f"'{cmd_without_prefix}' is not a function definition."
                    )

                defined_args = func_def.get("args", [])
                mapped_args = {}
                for arg_def in defined_args:
                    arg_name, arg_type = arg_def.split(":")
                    if arg_name not in args:
                        raise ConslyricRuntimeError(
                            f"Missing argument '{arg_name}' for function '{cmd_without_prefix}'"
                        )

                    arg_value = args[arg_name]
                    if arg_type == "num":
                        try:
                            mapped_args[arg_name] = float(arg_value)
                        except ValueError:
                            raise ConslyricRuntimeError(
                                f"Argument '{arg_name}' for function '{cmd_without_prefix}' must be a number, but got '{arg_value}'."
                            )
                    elif arg_type == "str":
                        mapped_args[arg_name] = str(arg_value)
                    else:
                        # Unknown type, just store as is
                        mapped_args[arg_name] = arg_value

                for func_cmd_item in func_def.get("run", []):
                    if isinstance(func_cmd_item, dict):
                        for func_cmd_key, func_cmd_val in func_cmd_item.items():
                            processed_func_cmd_val = {}
                            if isinstance(func_cmd_val, dict):
                                for k, v in func_cmd_val.items():
                                    if isinstance(v, str):
                                        # Use regex to find and replace ${arg_name} patterns
                                        def replace_arg(match):
                                            arg_name = match.group(1)
                                            if arg_name in mapped_args:
                                                return str(
                                                    mapped_args[arg_name]
                                                )
                                            else:
                                                raise ConslyricRuntimeError(
                                                    f"Undefined argument '{arg_name}' in function '{cmd_without_prefix}'"
                                                )

                                        processed_v = re.sub(
                                            r"\$\{(\w+)\}", replace_arg, v
                                        )
                                        processed_func_cmd_val[k] = processed_v
                                    else:
                                        processed_func_cmd_val[k] = v
                            else:
                                if isinstance(func_cmd_val, str):
                                    # Use regex to find and replace ${arg_name} patterns
                                    def replace_arg(match):
                                        arg_name = match.group(1)
                                        if arg_name in mapped_args:
                                            return str(mapped_args[arg_name])
                                        else:
                                            raise ConslyricRuntimeError(
                                                f"Undefined argument '{arg_name}' in function '{cmd_without_prefix}'"
                                            )

                                    processed_func_cmd_val = re.sub(
                                        r"\$\{(\w+)\}",
                                        replace_arg,
                                        func_cmd_val,
                                    )
                                else:
                                    processed_func_cmd_val = func_cmd_val

                            time_consumed += self._pre_calculate_command_time(
                                func_cmd_key,
                                processed_func_cmd_val,
                                current_state,
                            )
            else:
                self.logger.warning(
                    f"Unknown command during pre-calculation: {command_name}"
                )
        return time_consumed

    def _pre_calculate_total_time(self):
        """Pre-calculates the total expected time and checks against the time limit."""
        expected_time = 0.0
        current_state = {
            "current_show_duration": self._parse_time_string(
                self.data["metadata"]["showDefault"]
            ),
            "current_sleep_duration": self._parse_time_string(
                self.data["metadata"]["sleepDefault"]
            ),
            "current_effect": None,
            "current_text_color": None,
            "inplace_mode": False,
        }

        for item in self.data["run"]:
            if isinstance(item, str):
                line_duration = current_state["current_show_duration"]
                if (
                    current_state["current_effect"]
                    and current_state["current_effect"]["type"] == "typewriter"
                ):
                    line_duration = (
                        len(item) * current_state["current_effect"]["speed"]
                    )
                elif (
                    current_state["current_effect"]
                    and current_state["current_effect"]["type"] == "glitch"
                ):
                    line_duration = current_state["current_show_duration"]

                expected_time += line_duration
                expected_time += current_state["current_sleep_duration"]
            elif isinstance(item, dict):
                for command_name, args in item.items():
                    expected_time += self._pre_calculate_command_time(
                        command_name,
                        args if args is not None else {},
                        current_state,
                    )
            else:
                raise ConslyricRuntimeError(
                    f"Error: Unknown item type in 'text' sequence during pre-calculation: {type(item)}"
                )

        if expected_time > self.time_limit:
            raise ConslyricRuntimeError(
                f"Pre-calculated total time ({expected_time:.2f}s) exceeds time limit ({self.time_limit}s)."
            )
        self.logger.debug(
            f"Pre-calculated total time: {expected_time:.2f}s (within limit)"
        )

    def _execute_command(self, command_name: str, args: Dict[str, Any]):
        """Executes a Conslyric command."""
        if command_name.startswith("::cons:"):
            std_cmd_name = command_name[2:]
            if std_cmd_name in self.std_commands:
                self.std_commands[std_cmd_name](
                    self, **args
                )  # Pass self (interpreter instance)
            else:
                self.console.print(
                    f"[yellow]Warning: Unknown standard command: {command_name}[/yellow]"
                )
        elif command_name.startswith("::"):
            # Custom commands or internal commands
            cmd_without_prefix = command_name[2:]
            if cmd_without_prefix == "setShowRule":
                self._cmd_set_show_rule(args)
            elif cmd_without_prefix == "setSleepRule":
                self._cmd_set_sleep_rule(args)
            elif cmd_without_prefix == "endSection":
                self._cmd_end_section()
            elif cmd_without_prefix in self.defined_functions:
                self._execute_defined_function(cmd_without_prefix, args)
            else:
                self.console.print(
                    f"[yellow]Warning: Unknown command: {command_name}[/yellow]"
                )
        else:
            self.console.print(
                f"[red]Error: Invalid command format: {command_name}[/red]"
            )

    def _execute_defined_function(
        self, func_name: str, call_args: Dict[str, Any]
    ):
        """Executes a user-defined function."""
        func_def = self.defined_functions[func_name]
        if func_def.get("type") != "func":
            self.console.print(
                f"[red]Error: '{func_name}' is not a function definition.[/red]"
            )
            return

        # Validate and map arguments
        defined_args = func_def.get("args", [])
        mapped_args = {}
        for arg_def in defined_args:
            arg_name, arg_type = arg_def.split(":")
            if arg_name not in call_args:
                raise ConslyricRuntimeError(
                    f"Missing argument '{arg_name}' for function '{func_name}'"
                )
            # Basic type checking (can be expanded)
            if arg_type == "num" and not isinstance(
                call_args[arg_name], (int, float)
            ):
                raise ConslyricRuntimeError(
                    f"Argument '{arg_name}' for function '{func_name}' must be a number."
                )
            mapped_args[arg_name] = call_args[arg_name]

        # Execute commands in the function body
        for cmd_item in func_def.get("run", []):
            if isinstance(cmd_item, str):
                # This case should ideally not happen for commands in 'run'
                self.console.print(
                    f"[yellow]Warning: Unexpected string in function '{func_name}' run block: {cmd_item}[/yellow]"
                )
            elif isinstance(cmd_item, dict):
                for cmd_key, cmd_val in cmd_item.items():
                    # Replace placeholders like ${arg_name}
                    processed_cmd_val = {}
                    if isinstance(cmd_val, dict):
                        for k, v in cmd_val.items():
                            if isinstance(v, str):
                                # Use regex to find and replace ${arg_name} patterns
                                def replace_arg(match):
                                    arg_name = match.group(1)
                                    if arg_name in mapped_args:
                                        return str(mapped_args[arg_name])
                                    else:
                                        raise ConslyricRuntimeError(
                                            f"Undefined argument '{arg_name}' in function '{func_name}'"
                                        )

                                processed_v = re.sub(
                                    r"\$\{(\w+)\}", replace_arg, v
                                )
                                processed_cmd_val[k] = processed_v
                            else:
                                processed_cmd_val[k] = v
                    else:
                        if isinstance(cmd_val, str):
                            # Use regex to find and replace ${arg_name} patterns
                            def replace_arg(match):
                                arg_name = match.group(1)
                                if arg_name in mapped_args:
                                    return str(mapped_args[arg_name])
                                else:
                                    raise ConslyricRuntimeError(
                                        f"Undefined argument '{arg_name}' in function '{func_name}'"
                                    )

                            processed_cmd_val = re.sub(
                                r"\$\{(\w+)\}", replace_arg, cmd_val
                            )
                        else:
                            processed_cmd_val = cmd_val

                    self._execute_command(cmd_key, processed_cmd_val)

    def _cmd_set_show_rule(self, args: Dict[str, Any]):
        """Sets the show duration for the current lyric line."""
        duration_str = args.get("duration")
        if not duration_str:
            raise ConslyricRuntimeError(
                "::setShowRule requires 'duration' argument."
            )
        self.current_show_duration = self._parse_time_string(duration_str)

    def _cmd_set_sleep_rule(self, args: Dict[str, Any]):
        """Sets the sleep duration after the current lyric line."""
        duration_str = args.get("duration")
        if not duration_str:
            raise ConslyricRuntimeError(
                "::setSleepRule requires 'duration' argument."
            )
        self.current_sleep_duration = self._parse_time_string(duration_str)

    def _cmd_end_section(self):
        """Resets show and sleep rules to default."""
        self.current_show_duration = self._parse_time_string(
            self.data["metadata"]["showDefault"]
        )
        self.current_sleep_duration = self._parse_time_string(
            self.data["metadata"]["sleepDefault"]
        )
        self.console.print("[dim]Rules reset to default.[/dim]")

    def _apply_effects_and_print(self, text_content: str, duration: float):
        """Applies current effects and prints the text."""
        display_text = Text(
            text_content,
            style=self.current_text_color if self.current_text_color else "",
        )

        if self.current_effect and self.current_effect["type"] == "typewriter":
            speed = self.current_effect["speed"]
            calculated_duration = len(text_content) * speed
            self.total_elapsed_time += calculated_duration
            if self.total_elapsed_time > self.time_limit:
                raise ConslyricRuntimeError(
                    f"Time limit ({self.time_limit}s) exceeded during typewriter effect."
                )

            for i in range(len(text_content) + 1):
                if self.inplace_mode:
                    self.console.print(
                        display_text[:i], end="\r", overflow="crop"
                    )
                else:
                    self.console.print(
                        display_text[:i], end="\r", overflow="crop"
                    )  # Still use \r for typewriter effect
                time.sleep(speed)
            if not self.inplace_mode:
                self.console.print()  # Newline after typewriter if not in-place
        elif self.current_effect and self.current_effect["type"] == "glitch":
            intensity = self.current_effect["intensity"]
            # Simple glitch simulation: print text multiple times with random chars/colors
            for _ in range(intensity):
                glitched_text = "".join(
                    (
                        char
                        if random.random() > (intensity / 15.0)
                        else random.choice("!@#$%^&*()_+=-{}[]|\\:;\"'<>,.?/~`")
                    )
                    for char in text_content
                )
                glitch_color = random.choice(
                    ["red", "green", "blue", "magenta", "cyan", "yellow"]
                )
                self.console.print(
                    Text(glitched_text, style=glitch_color),
                    end="\r",
                    overflow="crop",
                )
                time.sleep(0.05)  # Small delay for glitch effect
            if self.inplace_mode:
                self.console.print(
                    display_text, end="\r", overflow="crop"
                )  # Final correct text
            else:
                self.console.print(display_text)
            self.total_elapsed_time += duration
            time.sleep(duration)  # Wait for the actual duration after glitch
        else:
            # No special effect
            if self.inplace_mode:
                self.console.print(display_text, end="\r", overflow="crop")
            else:
                self.console.print(display_text)
            self.total_elapsed_time += duration
            time.sleep(duration)

        if self.total_elapsed_time > self.time_limit:
            raise ConslyricRuntimeError(
                f"Time limit ({self.time_limit}s) exceeded."
            )

    def run(self):
        """Executes the Conslyric sequence."""
        self.logger.debug("--- Conslyric Playback Started ---")
        self.logger.debug(f"Time limit: {self.time_limit}s")

        # Pre-calculate total expected time
        self._pre_calculate_total_time()

        for item in self.data["run"]:
            if isinstance(item, str):
                # This is a lyric line
                self.logger.debug(
                    f"Displaying lyric: '{item}' for {self.current_show_duration}s"
                )
                self._apply_effects_and_print(item, self.current_show_duration)

                self.logger.debug(
                    f"Sleeping for {self.current_sleep_duration}s"
                )
                self.total_elapsed_time += self.current_sleep_duration
                if self.total_elapsed_time > self.time_limit:
                    raise ConslyricRuntimeError(
                        f"Time limit ({self.time_limit}s) exceeded during sleep."
                    )
                time.sleep(self.current_sleep_duration)

            elif isinstance(item, dict):
                # This is a command
                for command_name, args in item.items():
                    self.logger.debug(
                        f"Executing command: {command_name} with args: {args}"
                    )
                    self._execute_command(
                        command_name, args if args is not None else {}
                    )
            else:
                self.logger.fatal(
                    f"Error: Unknown item type in 'text' sequence: {type(item)}"
                )

        self.logger.debug("--- Conslyric Playback Finished ---")
        self.logger.debug(f"Total elapsed time: {self.total_elapsed_time:.2f}s")
