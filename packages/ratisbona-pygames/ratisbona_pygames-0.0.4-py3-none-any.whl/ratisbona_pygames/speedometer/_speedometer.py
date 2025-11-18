from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, DefaultDict, Optional

import numpy as np
import pygame
import serial

from ratisbona_pygames.gameutils import Game, FPSCounter, Background, GameElement, Debounce

MAX_RPM_SPEED = {0: 0, 1: 60, 2: 100, 3: 140, 4: 190, 5: 230}

def rechteckwelle(
        frequenz_hz: float, dauer_sec: float,
        sample_rate_hz=44100, normalized_volume=0.5
) -> np.ndarray:
    """
    Creates a square wave signal with the specified frequency and duration at the given sample rate.

    Args:
        frequenz_hz (float): Frequency of the square wave in Hertz.
        dauer_sec (float): Duration of the signal in seconds.
        sample_rate_hz (int): Sample rate in Hertz (default is 44100).
        normalized_volume (float): Volume level normalized between 0 and 1 (default is 0.5).

    Returns:
         samples (np.ndarray): An array of int16 samples representing the square wave signal.

    """
    t = np.linspace(0, dauer_sec, int(sample_rate_hz * dauer_sec), endpoint=False)
    signal = 0.5 * normalized_volume * np.sign(np.sin(2 * np.pi * frequenz_hz * t))
    samples = np.int16(signal * 32767)
    return samples

def detect_joystick():
    """
    Detects the first available joystick and initializes it.

    Returns:
        pygame.joystick.Joystick | None: The initialized joystick object if found, otherwise None.
    """
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print("Joystick detected:", joystick.get_name())
        return joystick
    print("No joystick detected.")
    return None

@dataclass
class JoystickTracker:#
    """
    Tracks joystick events and maintains the state of axes and buttons.

    Attributes:
        joystick (pygame.joystick.Joystick): The joystick object to track. Best use `detect_joystick()` to get a joystick.
        axis_values (dict[int, float]): Dictionary to hold axis values.
        buttons_values (dict[int, bool]): Dictionary to hold button states.
        press_listeners (DefaultDict[int, list[Callable[[], None]]]): Listeners for button press events.
    """
    joystick: Optional[pygame.joystick.Joystick] = None
    axis_values: dict[int, float] = field(default_factory=dict)
    buttons_values: dict[int, bool] = field(default_factory=dict)
    press_listeners: dict[int, list[Callable[[], None]]] = field(default_factory=lambda: defaultdict(list))

    def receive_event(self, event):
        if event.type == pygame.JOYAXISMOTION:
            print(f"Axis {event.axis} moved to {event.value:.2f}")
            self.axis_values[event.axis] = event.value
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"Button {event.button} pressed")
            for listener in self.press_listeners.get(event.button, []):
                listener()
            self.buttons_values[event.button] = True
        elif event.type == pygame.JOYBUTTONUP:
            print(f"Button {event.button} released")
            self.buttons_values[event.button] = False


class MotorSound:
    """
    Class to generate and control a motor sound based on RPM.

    Attributes:
        sample_rate (int): Sample rate for sound generation.
        _sound (pygame.mixer.Sound): The generated sound object.
        _channel (pygame.mixer.Channel): The channel to play the sound on.

    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self._channel = None
        self._sound = None
        self._freq = None

    def set_frequenz(self, freq):
        """
        Sets the frequency of the motor sound.

        Args:
            freq (float): Frequency in Hz to set for the motor sound.

        Returns:
            None

        Side Effects:
            If the frequency is less than 1, the sound will stop.
            If the frequency changes, a new sound will be generated and played.
        """
        if self._freq == freq:
            return
        self._freq = freq

        if freq < 1:
            self.stop()
            return

        period = 1 / freq
        samples = rechteckwelle(freq, period, self.sample_rate)
        self._sound = pygame.sndarray.make_sound(samples)

        if self._channel:
            self._channel.stop()

        self._channel = self._sound.play(loops=-1)

    def stop(self):
        if self._channel:
            self._channel.stop()


@dataclass
class Motorbike:
    """
    Represents a motorbike with properties for speed, acceleration, gear, and RPM.

    Attributes:
        velocity_km_h (float): Current speed in km/h.
        accelleration_m_s2 (float): Acceleration in m/s².
        gear (int): Current gear (0-5).
        rpm (int): Current RPM based on speed and gear (readonly)
    """
    velocity_km_h: float = 0.0
    accelleration_m_s2: float = 5
    gear: int = 0

    def shift_up(self):
        """
        Shifts the gear up by one, if not already in the highest gear (5).
        """
        if self.gear < 5:
            self.gear += 1

    def shift_down(self):
        """
        Shifts the gear down by one, if not already in the lowest gear (0).
        :return:
        """
        if self.gear > 0:
            self.gear -= 1

    @property
    def rpm(self):
        """
        Calculates the RPM based on the current speed and gear.

        Returns:
            int: The calculated RPM. Returns 0 if the gear is 0, otherwise calculates based on speed and gear.
        """
        if self.gear == 0:
            return 1000

        rpm = int(self.velocity_km_h / MAX_RPM_SPEED[self.gear] * 12000)

        #print(f"Calculating RPM: velocity_km_h={self.velocity_km_h}, gear={self.gear}, rpm={rpm}")
        if rpm < 500:
            return 0
        if rpm < 1000:
            return 1000
        return rpm


    def update_velocity(self, dt: float, accelerate: bool = True):
        """
        Updates the velocity of the motorbike based on the acceleration and time delta.
        Calls this method with `dt` from the game loop to update the speed in the tick-event!

        Parameters:
            dt (float): Time delta in milli-seconds since the last update.
            accelerate (bool): If True, increases speed; if False, decreases speed.
        """
        delta = self.accelleration_m_s2 * dt * 3.6  # Convert m/s to km/h

        if accelerate:
            if self.gear > 0:
                self.velocity_km_h += delta
        else:
            self.velocity_km_h -= delta
            if self.velocity_km_h < 0:
                self.velocity_km_h = 0

@dataclass
class TachometerController:
    """
    Controls the tachometer by sending commands to a serial interface.

    Attributes:
        serial (serial.Serial): The serial interface to communicate with the tachometer.
        _rpm (int): Current RPM value.
        _speed (int): Current speed in km/h.
        _gear (int): Current gear.
    """
    serial: serial.Serial
    _rpm: int = 0
    _speed: int = 0
    _gear: int = 0

    def empty_buffer(self):
        """
        Empties the serial buffer by reading all available responses, echoing them to the console.
        """
        while self.serial.in_waiting:
            text = self.serial.read(self.serial.in_waiting).decode('utf-8')
            print("Emptying buffer:", text)

    def set_gear(self, gear: int):
        """
        Sets the gear of the motorbike and sends the command to the serial interface.

        Args:
            gear (int): The gear to set (0-5).
        Returns:
            None
        """
        if self._gear == gear:
            return
        self._gear = gear
        self.serial.write(f"4,{gear};\n".encode('utf-8'));

    def set_speed(self, speed: int):
        """
        Sets the speed of the motorbike and sends the command to the serial interface.

        Args:
            speed (int): The speed in km/h to set.

        Returns:
            None
        """
        if self._speed == speed:
            return
        self._speed = speed
        self.serial.write(f"0,{speed};\n".encode('utf-8'))

    def set_rpm(self, rpm: int):
        if self._rpm == rpm:
            return
        self._rpm = rpm
        self.serial.write(f"1,{rpm};\n".encode('utf-8'))



@dataclass
class MotorbikeElement:
    game: Game
    font: pygame.font.Font
    joystick_tracker: JoystickTracker | None = None
    motor_sound: MotorSound | None = None
    tacho_controller: TachometerController | None = None
    motorbike: Motorbike = field(default_factory=Motorbike)

    def press_listener(self):
        if self.joystick_tracker.axis_values.get(1, 0) < -0.1:
            self.motorbike.shift_up()
        else:
            self.motorbike.shift_down()

    def __post_init__(self):

        if self.joystick_tracker:
            print(self.joystick_tracker.press_listeners)
            self.joystick_tracker.press_listeners[0].append(self.press_listener)


    def render(self):
        if self.tacho_controller:
            # Send current state to the serial interface
            self.tacho_controller.set_speed(int(self.motorbike.velocity_km_h))
            self.tacho_controller.set_rpm(self.motorbike.rpm)
            self.tacho_controller.set_gear(self.motorbike.gear)
            self.tacho_controller.empty_buffer()

        if self.motor_sound:
            # Update the motor sound based on the current RPM
            self.motor_sound.set_frequenz(self.motorbike.rpm / 60 * 2)

        # Render the speedometer
        speed_text = f"Speed: {self.motorbike.velocity_km_h:.1f} km/h"
        rpm_text = f"RPM: {self.motorbike.rpm}"
        gear_text = f"Gear: {self.motorbike.gear}"


        speed_surface = self.font.render(speed_text, True, "white")
        rpm_surface = self.font.render(rpm_text, True, "white")
        gear_surface = self.font.render(gear_text, True, "white")

        self.game.screen.blit(speed_surface, (10, 10))
        self.game.screen.blit(rpm_surface, (10, 40))
        self.game.screen.blit(gear_surface, (10, 70))

    def tick(self):
        if self.game.keys[pygame.K_UP] or self.joystick_tracker.axis_values.get(1, 0) < -0.1:
            self.motorbike.update_velocity(self.game.dt, accelerate=True)

        elif self.game.keys[pygame.K_DOWN] or self.joystick_tracker.axis_values.get(1, 0) > 0.1:
            self.motorbike.update_velocity(self.game.dt, accelerate=False)




def speedometer_main():

    # Serielle Schnittstelle öffnen (z. B. COM3 unter Windows oder /dev/ttyUSB0 unter Linux)
    ser = None
    try:
        ser = serial.Serial(
            port='/dev/ttyUSB0',  # oder 'COM3' unter Windows
            baudrate=115200,
            timeout=1  # Sekunde(n) warten auf Antwort
        )
    except serial.SerialException as e:
        print(f"Fehler beim Öffnen der seriellen Schnittstelle: {e}")

    sample_rate = 44100
    pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=1)

    game = Game((1024, 768), "Speedometer Demo", fps=50)
    joystick = detect_joystick()
    joystick_tracker = None
    if joystick:
        joystick_tracker = JoystickTracker(joystick)
        game.event_listeners.append(joystick_tracker.receive_event)

    font = pygame.font.SysFont("Noto sans", 20)

    background = Background(game, (0x99, 0x99, 0x99))
    game.renderers.append(background.render)

    fps = FPSCounter(game, font)
    game.renderers.append(fps.render)
    game.tickers.append(fps.tick)

    motorsound = MotorSound(sample_rate)
    controller = TachometerController(ser) if ser else None

    motorbike = MotorbikeElement(game, font, joystick_tracker, motorsound, controller)
    game.renderers.append(motorbike.render)
    game.tickers.append(motorbike.tick)

    shift_up = Debounce(
        game, pygame.K_RIGHT, motorbike.motorbike.shift_up
    )
    game.tickers.append(shift_up.tick)
    shift_down = Debounce(
        game, pygame.K_LEFT, motorbike.motorbike.shift_down
    )
    game.tickers.append(shift_down.tick)

    game.run()
