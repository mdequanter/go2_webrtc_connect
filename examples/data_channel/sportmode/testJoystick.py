import pygame
import time

# Initialiseer pygame
pygame.init()

# Kijk of er een joystick beschikbaar is
if pygame.joystick.get_count() == 0:
    print("Geen joystick gevonden. Sluit een joystick aan en probeer opnieuw.")
else:
    # Selecteer de eerste beschikbare joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Verbonden met joystick: {joystick.get_name()}")

    # Houd de vorige status van de knoppen en assen bij om veranderingen te detecteren
    previous_buttons = [0] * joystick.get_numbuttons()
    previous_axes = [0.0] * joystick.get_numaxes()
    previous_hats = [(0, 0)] * joystick.get_numhats()

    try:
        while True:
            # Controleer pygame-events (zoals joystickbewegingen)
            pygame.event.pump()

            # Controleer veranderingen in de knoppen
            for i in range(joystick.get_numbuttons()):
                button = joystick.get_button(i)
                if button != previous_buttons[i]:  # Alleen toon veranderingen
                    print(f"Knop {i} is nu {'ingedrukt' if button else 'losgelaten'}")
                    previous_buttons[i] = button

            # Controleer veranderingen in de assen
            for i in range(joystick.get_numaxes()):
                axis = joystick.get_axis(i)
                if abs(axis - previous_axes[i]) > 0.1:  # Toon alleen significante veranderingen
                    print(f"As {i} waarde: {axis:.2f}")
                    previous_axes[i] = axis

            # Controleer veranderingen in de hats (D-Pad)
            for i in range(joystick.get_numhats()):
                hat = joystick.get_hat(i)
                if hat != previous_hats[i]:  # Alleen toon veranderingen
                    print(f"Hat {i} waarde: {hat}")
                    previous_hats[i] = hat

            # Kort wachten om overbelasting van de CPU te voorkomen
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Programma beëindigd door gebruiker")

    # Joystick afsluiten
    joystick.quit()
    pygame.quit()
