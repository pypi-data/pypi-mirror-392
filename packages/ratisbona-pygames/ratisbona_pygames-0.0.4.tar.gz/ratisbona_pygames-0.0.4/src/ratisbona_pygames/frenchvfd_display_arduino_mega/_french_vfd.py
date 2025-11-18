from __future__ import annotations

from asyncio import sleep
import time as timelib
from dataclasses import field, dataclass
from datetime import time, date
from typing import Callable, ClassVar, Dict


@dataclass
class FrenchVFD:
    _HOUR_DIGIT0: ClassVar[int] = 2
    _HOUR_DIGIT1: ClassVar[int] = 3
    _MINUTE_DIGIT0: ClassVar[int] = 4
    _MINUTE_DIGIT1: ClassVar[int] = 5
    _SECOND_DIGIT0: ClassVar[int] = 6
    _SECOND_DIGIT1: ClassVar[int] = 7
    _MONTH_DIGIT0: ClassVar[int] = 8
    _MONTH_DIGIT1: ClassVar[int] = 9
    _DAY_DIGIT0: ClassVar[int] = 10
    _DAY_DIGIT1: ClassVar[int] = 11
    _COMMANDS: ClassVar[str] = [
        "FIN", "CH2", "CH1", "O=O", "DUB", "VPS", "PRG", "MIX", "VHS", "DEB",
        "[5]", "[4]", "NOC", "HIF", "SEC", "L=D", "DAT", "PAL", "SAT", "ENR",
        "[3]",
        "[6]",
        "[7]", "[8]",
        "[1]", "[2]", "PSE", "REW", "PLY", "FWD",
        "DPT"
    ]

    message_callback: Callable[[str], None]
    _digits: int[12] = field(default_factory=lambda: [None] * 12)
    _the_functions: Dict[str, bool] = field(default_factory=lambda: {cmd: False for cmd in FrenchVFD._COMMANDS})

    def get_command_state(self, command: str) -> bool:
        if command not in self._functions:
            raise ValueError(f"Command {command} not recognized")
        return self._functions[command]

    def set_command_state(self, command: str, state: bool):
        if command not in self._the_functions:
            raise ValueError(f"Command {command} not recognized")
        if self._the_functions[command] == state:
            return
        self._emit_command_message(command, state)
        self._the_functions[command] = state

    def toggle_command_state(self, command: str):
        if command not in self._the_functions:
            raise ValueError(f"Command {command} not recognized")
        state = not self._the_functions[command]
        self.set_command_state(command, state)

    def get_digit(self, digit_number: int) -> int:
        if digit_number < 0 or digit_number >= len(self._digits):
            raise IndexError("Digit number out of range")
        return self._digits[digit_number]

    def set_digit(self, digit_number: int, value: int):
        if digit_number < 0 or digit_number >= len(self._digits):
            raise IndexError("Digit number out of range")
        if value < 0 or value > 9:
            raise ValueError("Value must be between 0 and 9")
        if self._digits[digit_number] is not None and self._digits[digit_number] == value:
            return
        self._emit_digit_message(digit_number, value)
        self._digits[digit_number] = value

    def _emit_digit_message(self, digit_number: int, value: int):
        message = f"4,{digit_number},{value};\n"
        self.message_callback(message)

    def _emit_command_message(self, command: str, state: bool):
        message = f"6,{command},{int(state)};\n"
        self.message_callback(message)

    def set_double_digit(self, digit0: int, digit1: int, value: int):
        first_digit = value // 10
        second_digit = value % 10
        self.set_digit(digit0, first_digit)
        self.set_digit(digit1, second_digit)

    def set_quadruple_digit(self, digit0: int, digit1: int, digit2: int, digit3:int, value: int):
        first_digit = value // 1000
        second_digit = (value % 1000) // 100
        third_digit = (value % 100) // 10
        forth_digit = (value % 10)

        self.set_digit(digit0, first_digit)
        self.set_digit(digit1, second_digit)
        self.set_digit(digit2, third_digit)
        self.set_digit(digit3, forth_digit)


    def display_time(self, the_time: time):
        """
        Display the time on the French VFD.

        Args:
            the_time (datetime): The time to display.
            french_vfd (FrenchVFD): The French VFD object.
        """
        self.set_double_digit(
            FrenchVFD._HOUR_DIGIT0, FrenchVFD._HOUR_DIGIT1, the_time.hour
        )
        self.set_double_digit(
            FrenchVFD._MINUTE_DIGIT0, FrenchVFD._MINUTE_DIGIT1, the_time.minute
        )
        self.set_double_digit(
            FrenchVFD._SECOND_DIGIT0, FrenchVFD._SECOND_DIGIT1, the_time.second
        )

    def display_date(self, the_date: date):
        self.set_double_digit(
            FrenchVFD._MONTH_DIGIT0, FrenchVFD._MONTH_DIGIT1, the_date.month
        )
        self.set_double_digit(
            FrenchVFD._DAY_DIGIT0, FrenchVFD._DAY_DIGIT1, the_date.day
        )

    def toggle_colon(self):
        """
        Toggle the colon on the French VFD.

        Args:
            french_vfd (FrenchVFD): The French VFD object.
        """
        self.toggle_command_state("DPT")

