import pygame

from ratisbona_pygames.gameutils import Game


def joystick_demo_main():

    game = Game((640, 480), "Joystick Demo")
    import pygame

    pygame.init()
    pygame.joystick.init()

    # Joystick finden und initialisieren
    if pygame.joystick.get_count() == 0:
        print("Kein Joystick erkannt!")
        exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Joystick erkannt: {joystick.get_name()}")
    print(f"Achsen: {joystick.get_numaxes()}")
    print(f"Buttons: {joystick.get_numbuttons()}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.JOYAXISMOTION:
                axis = event.axis
                value = event.value  # zwischen -1.0 und +1.0
                print(f"Achse {axis}: {value:.2f}")

            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"Button {event.button} gedrückt")

            elif event.type == pygame.JOYBUTTONUP:
                print(f"Button {event.button} losgelassen")

    pygame.quit()
