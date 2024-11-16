import asyncio
import logging
import sys
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
import numpy as np
import json
import matplotlib.pyplot as plt

# Variabelen om de robotpositie bij te houden
robot_x, robot_y, robot_y = None, None, None

import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt

def plot_point_cloud(ax, positions, robot_x=None, robot_y=None, robot_w=None):
    """
    Visualiseer een 2D-puntwolk op basis van x- en y-coördinaten,
    en voeg een bolletje toe op een specifieke positie en detecteer objecten binnen een straal van 25 cm.

    :param ax: De as van de bestaande figuur.
    :param positions: Een numpy-array van vorm (n, 3) met de x-, y-, z-coördinaten van punten.
    :param robot_x: De x-coördinaat van de robot.
    :param robot_y: De y-coördinaat van de robot.
    :param robot_w: De richting van de robot in radialen.
    """
    ax.clear()

    posOnMapX = 60
    posOnMapY = 60 - robot_y

    # Filter de punten die zich vooraan bevinden (bijvoorbeeld: alleen punten met een positieve x-waarde)
    front_positions = positions[(positions[:, 2] >= 15) & (positions[:, 2] <= 20)]
    
    # Plot alleen de x- en y-coördinaten van de gefilterde puntwolk
    ax.scatter(front_positions[:, 0], front_positions[:, 1], color='blue', s=1, label='Points')

    # Voeg een bolletje toe op het punt (60, 60)
    ax.scatter(posOnMapX, posOnMapY, color='green', s=50, label='Robot Position')  # Groen bolletje op (60, 60)


    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('2D Point Cloud')
    plt.legend()
    plt.draw()
    plt.pause(0.2)




# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)
    
async def main():
    global robot_x, robot_y,robot_w  # Maak de robotpositie beschikbaar in main()

    try:
        # Kies een connectiemethode (de correcte decommentariëren)
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="unitree.local")

        # Maak verbinding met de WebRTC-service.
        await conn.connect()

        # Schakel de verkeersbesparingsmodus op het datakanaal uit.
        await conn.datachannel.disableTrafficSaving(True)

        # Publiceer een bericht om de LIDAR-sensor in te schakelen.
        conn.datachannel.pub_sub.publish_without_callback("rt/utlidar/switch", "on")

        # Maak de figuur en as aan buiten de callback-functie
        fig, ax = plt.subplots(figsize=(10, 7))

        # Definieer een callback-functie om LIDAR-berichten te verwerken wanneer deze worden ontvangen.
        def lidar_callback(message):
            # Print de data ontvangen van de LIDAR-sensor.
            data = message["data"]
            positions = data['data']['positions']
            positions = positions.reshape(-1, 3)

            # Visualisatie aanroepen met de huidige robotpositie
            plot_point_cloud(ax, positions, robot_x, robot_y, robot_w)

        def pose_callback(message):
            # Update de robotpositie met de ontvangen waarden
            global robot_x, robot_y, robot_w
            robot_x = message['data']['pose']['position']['x']
            robot_y = message['data']['pose']['position']['y']
            robot_w = message['data']['pose']['orientation']['w']
            #print(f"x: {robot_x}, y: {robot_y}, w: {robot_w}")
  
        # Abonneer op de LIDAR voxel map data en gebruik de callback-functie om inkomende berichten te verwerken.
        conn.datachannel.pub_sub.subscribe("rt/utlidar/voxel_map_compressed", lidar_callback)
        conn.datachannel.pub_sub.subscribe("rt/utlidar/robot_pose", pose_callback)
        
        # Houd het programma draaiende om gebeurtenisverwerking mogelijk te maken voor 1 uur.
        await asyncio.sleep(3600)

    except ValueError as e:
        # Log eventuele waarde fouten die optreden tijdens het proces.
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Behandel Ctrl+C om netjes af te sluiten.
        print("\nProgram interrupted by user")
        sys.exit(0)
