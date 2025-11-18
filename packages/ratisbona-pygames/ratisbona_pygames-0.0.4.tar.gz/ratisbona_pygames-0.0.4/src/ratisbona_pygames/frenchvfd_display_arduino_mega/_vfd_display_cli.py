import time as timelib
from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Callable, TypeVar

import psutil
from serial import Serial

from ratisbona_utils.state_machine import State, StateMachine
from ratisbona_utils.statistics import RunningAverage
from ._french_vfd import FrenchVFD
from ..gameutils import run_precise_millisecond_timer, LarsonScanner

TIMEOUT = 1.0  # seconds


def reset_arduino(ser: Serial):
    print("No response — resetting Arduino...")
    ser.setDTR(False)
    timelib.sleep(0.1)
    ser.setDTR(True)
    timelib.sleep(2)  # Give Arduino time to reboot


def send_and_wait_for_response(ser, message):
    ser.reset_input_buffer()
    ser.write(message.encode("utf-8"))
    print("Sent:", message.strip())

    start_time = timelib.time()
    while timelib.time() - start_time < TIMEOUT:
        if ser.in_waiting:
            response = ser.readline().decode("utf-8").strip()
            print("Recv:", response)
            return True
        timelib.sleep(0.01)  # Small delay


def transmit(ser: Serial, message: str):
    """
    Transmit a message to the Arduino and wait for a response.

    Args:
        ser (Serial): The serial connection to the Arduino.
        message (str): The message to transmit.

    Returns:
        bool: True if a response was received, False otherwise.
    """
    if not send_and_wait_for_response(ser, message):
        reset_arduino(ser)
        return send_and_wait_for_response(ser, message)
    return True


def vfd_display_cli():
    PORT = "/dev/ttyACM0"  # or 'COM3' on Windows
    BAUDRATE = 115200  # Adjust as needed

    with Serial(PORT, BAUDRATE, timeout=1) as ser:
        timelib.sleep(1)  # Wait for arduino to boot (reboots on connection)

        french_vfd = FrenchVFD(lambda message: transmit(ser, message))

        # CPU load, flasher for it and seconds flasher
        cpu_load_percent = RunningAverage(100)
        sec_flash = valchange_flash(
            trigger_callback=lambda: french_vfd.set_command_state("SEC", True),
            revoke_callback=lambda: french_vfd.set_command_state("SEC", False),
            num_ticks=1,
        )
        pal_flash = valchange_flash(
            trigger_callback=lambda: french_vfd.set_command_state("PAL", True),
            revoke_callback=lambda: french_vfd.set_command_state("PAL", False),
            num_ticks=1,
        )
        netw_read_flash = valchange_flash(
            trigger_callback=lambda: french_vfd.set_command_state("L=D", True),
            revoke_callback=lambda: french_vfd.set_command_state("L=D", False),
            num_ticks=1,
        )
        netw_write_flash = valchange_flash(
            trigger_callback=lambda: french_vfd.set_command_state("SAT", True),
            revoke_callback=lambda: french_vfd.set_command_state("SAT", False),
            num_ticks=1,
        )


        # State machines for lower display
        num_ticks = 100
        date_state = DateState(french_vfd=french_vfd, num_ticks=num_ticks)
        running_processes_state = RunningProcessesState(
            french_vfd=french_vfd, num_ticks=num_ticks
        )
        network_input_state = NetworkTrafficState(
            french_vfd=french_vfd, num_ticks=num_ticks
        )
        network_output_state = NetworkTrafficState(
            french_vfd=french_vfd, num_ticks=num_ticks, show_transmitted=True
        )
        date_state.next_state = running_processes_state
        running_processes_state.next_state = network_input_state
        network_input_state.next_state = network_output_state
        network_output_state.next_state = date_state
        lower_display_state = StateMachine(initial_state=date_state)

        # Program Squares light effect
        larson_scanner = LarsonScanner(
            num_lights=8, extra_border=3, trailing_lights=3,
            callback=lambda light, onoff: french_vfd.set_command_state(f"[{light+1}]", onoff)
        )

        # The display Frames, 100ms per frame = 10 FPS refresh
        def on_frame(milliseconds: int):
            french_vfd.display_time(datetime.now().time())

            if milliseconds % 1000 == 0:
                french_vfd.toggle_colon()

            if milliseconds % 500 == 0:
                larson_scanner.cycle()

            sec_flash(milliseconds // 1000)

            cpu_load_percent.add_sample(psutil.cpu_percent(interval=None))
            french_vfd.set_double_digit(0, 1, pal_flash(int(cpu_load_percent.mean())))
            counters = psutil.net_io_counters()
            netw_read_flash(counters.bytes_recv >> 10)
            netw_write_flash(counters.bytes_sent >> 10)

            lower_display_state.tick()

        run_precise_millisecond_timer(on_frame, 100)


@dataclass
class TickBasedState(State):
    num_ticks: int
    _num_ticks_to_go: int = 0

    def state_entered(self):
        self._num_ticks_to_go = self.num_ticks

    def state_left(self):
        pass

    def tick(self):
        self._num_ticks_to_go -= 1

    def transition(self):
        if self._num_ticks_to_go > 0:
            return None
        return self.next_state


@dataclass
class NetworkTrafficState(TickBasedState):
    french_vfd: FrenchVFD = None
    show_transmitted: bool = False

    def state_entered(self):
        super().state_entered()
        self.french_vfd.set_command_state("REW" if self.show_transmitted else "FWD", True)

    def state_left(self):
        super().state_left()
        self.french_vfd.set_command_state("REW" if self.show_transmitted else "FWD", False)

    def tick(self):
        super().tick()
        counters = psutil.net_io_counters()
        number = counters.bytes_sent if self.show_transmitted else counters.bytes_recv
        number >>= 20  # Megabytes wanted
        number %= 10000  # Limit to 4 digits
        self.french_vfd.set_quadruple_digit(8, 9, 10, 11, number)


@dataclass
class RunningProcessesState(TickBasedState):
    french_vfd: FrenchVFD = None

    def state_entered(self):
        super().state_entered()
        self.french_vfd.set_command_state("PRG", True)

    def state_left(self):
        super().state_left()
        self.french_vfd.set_command_state("PRG", False)

    def tick(self):
        super().tick()
        self.french_vfd.set_quadruple_digit(8, 9, 10, 11, number_of_processes())


@dataclass
class DateState(TickBasedState):
    french_vfd: FrenchVFD = None

    def state_entered(self):
        super().state_entered()
        self.french_vfd.set_command_state("DAT", True)

    def state_left(self):
        super().state_left()
        self.french_vfd.set_command_state("DAT", False)

    def tick(self):
        super().tick()
        self.french_vfd.display_date(datetime.now().date())


T = TypeVar("T")


def valchange_flash(
    trigger_callback: Callable[[], None] | None = None,
    revoke_callback: Callable[[], None] | None = None,
    num_ticks: int = 1,
):
    last_value = None
    flash = Flash(
        trigger_callback=trigger_callback,
        revoke_callback=revoke_callback,
        num_ticks=num_ticks,
    )

    def wrapped(value: T) -> T:
        nonlocal last_value
        flash.tick()
        if value != last_value:
            flash.flash()
            last_value = value
        return value

    return wrapped


@dataclass
class Flash:
    trigger_callback: Callable[[], None] | None = None
    revoke_callback: Callable[[], None] | None = None
    num_ticks: int = 1
    _num_ticks_to_go: int = 0

    def flash(self=None):
        if self.trigger_callback is not None:
            self.trigger_callback()
        self._num_ticks_to_go = self.num_ticks

    def tick(self):
        if self._num_ticks_to_go > 0:
            self._num_ticks_to_go -= 1
            if self._num_ticks_to_go == 0 and self.revoke_callback is not None:
                self.revoke_callback()


def number_of_processes():
    running = 0
    for proc in psutil.process_iter(["status"]):
        try:
            if proc.info["status"] == psutil.STATUS_RUNNING:
                running += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return running
