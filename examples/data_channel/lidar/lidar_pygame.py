import asyncio
import logging
import sys
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
import numpy as np
import json

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def plot_point_cloud(ax, positions, indices=None):
    """
    Visualiseer een 3D-puntwolk en (optioneel) vlakken op basis van posities en indices.
    
    :param ax: De as van de bestaande figuur.
    :param positions: Een numpy-array van vorm (n, 3) met de x-, y-, z-coördinaten van punten.
    :param indices: Optionele numpy-array van indices om vlakken te definiëren.
    """
    ax.clear()
    
    # Filter de punten die zich vooraan bevinden (bijvoorbeeld: alleen punten met een positieve x-waarde)
    front_positions = positions
    
    # Plot de punten uit de gefilterde puntwolk
    ax.scatter(front_positions[:, 0], front_positions[:, 1], front_positions[:, 2], color='blue', s=2, label='Points')
    #ax.scatter(front_positions[:, 0], front_positions[:, 1], color='blue', s=2, label='Points')

    if indices is not None:
        # Zorg dat indices een 2D-array is met drie indices per vlak
        if indices.shape[1] == 3:
            faces = [[front_positions[indices[i, 0]], front_positions[indices[i, 1]], front_positions[indices[i, 2]]] for i in range(indices.shape[0]) if indices[i, 0] < len(front_positions) and indices[i, 1] < len(front_positions) and indices[i, 2] < len(front_positions)]
            face_collection = Poly3DCollection(faces, alpha=0.3, edgecolor='grey')
            ax.add_collection3d(face_collection)
        else:
            print("Error: Indices should have three columns for defining triangular faces.")

    # Dynamisch de limieten instellen op basis van de data
    ax.set_xlim(front_positions[:, 0].min(), front_positions[:, 0].max())
    ax.set_ylim(front_positions[:, 1].min(), front_positions[:, 1].max())
    ax.set_zlim(front_positions[:, 2].min(), front_positions[:, 2].max())

    # Zet de view zodanig dat de map van bovenaf bekeken wordt
    ax.view_init(elev=50, azim=30)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Point Cloud and Faces')
    plt.legend()
    plt.draw()
    plt.pause(0.01)

# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)
    
async def main():
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
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')


        def pose_callback(message):
            # Print de data ontvangen van de LIDAR-sensor.
            x = message['data']['pose']['position']['x']
            y = message['data']['pose']['position']['y']
            w = message['data']['pose']['orientation']['w']
            print (f"x: {x},  y: {y}, w: {w}")
  

        # Definieer een callback-functie om LIDAR-berichten te verwerken wanneer deze worden ontvangen.
        def lidar_callback(message):
            # Print de data ontvangen van de LIDAR-sensor.
            data = message["data"]
            positions = data['data']['positions']
            positions = positions.reshape(-1, 3)

            indices = np.random.randint(0, len(positions), (30, 3))  # Zorg dat dit een (n, 3)-array is

            # Visualisatie aanroepen
            plot_point_cloud(ax, positions, None)

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
