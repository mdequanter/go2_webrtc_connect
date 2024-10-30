import asyncio
import logging
import sys
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
import numpy as np
import json

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def plot_point_cloud(positions, indices=None):
    """
    Visualiseer een 3D-puntwolk en (optioneel) vlakken op basis van posities en indices.
    
    :param positions: Een numpy-array van vorm (n, 3) met de x-, y-, z-coördinaten van punten.
    :param indices: Optionele numpy-array van indices om vlakken te definiëren.
    """

    print (f"plotting {positions}")
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot de punten uit de puntwolk
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], color='blue', s=2, label='Points')

    if indices is not None:
        # Zorg dat indices een 2D-array is met drie indices per vlak
        if indices.shape[1] == 3:
            faces = [[positions[indices[i, 0]], positions[indices[i, 1]], positions[indices[i, 2]]] for i in range(indices.shape[0])]
            face_collection = Poly3DCollection(faces, alpha=0.3, edgecolor='grey')
            ax.add_collection3d(face_collection)
        else:
            print("Error: Indices should have three columns for defining triangular faces.")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Point Cloud and Faces')
    plt.legend()
    plt.show()


# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)
    
async def main():
    try:
        # Choose a connection method (uncomment the correct one)
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber="B42D2000XXXXXXXX")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.Remote, serialNumber="B42D2000XXXXXXXX", username="email@gmail.com", password="pass")
        #conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)

        # Connect to the WebRTC service.
        await conn.connect()

        # Disable traffic saving mode on the data channel.
        await conn.datachannel.disableTrafficSaving(True)

        # Publish a message to turn the LIDAR sensor on.
        conn.datachannel.pub_sub.publish_without_callback("rt/utlidar/switch", "on")



        # Define a callback function to handle LIDAR messages when received.
        def lidar_callback(message):
            # Print the data received from the LIDAR sensor.
            data = message["data"]
            positions = data['data']['positions']
            positions = positions.reshape(-1, 3)

            indices = np.random.randint(0, 100, (30, 3))  # Zorg dat dit een (n, 3)-array is

            # Visualisatie aanroepen
            plot_point_cloud(positions, indices)
            #input("wait")

            
                

        # Subscribe to the LIDAR voxel map data and use the callback function to process incoming messages.
        conn.datachannel.pub_sub.subscribe("rt/utlidar/voxel_map_compressed", lidar_callback)
        #conn.datachannel.pub_sub.subscribe("rt/utlidar/voxel_map", lidar_callback)

        
        # Keep the program running to allow event handling for 1 hour.
        await asyncio.sleep(3600)
    
    except ValueError as e:
        # Log any value errors that occur during the process.
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C to exit gracefully.
        print("\nProgram interrupted by user")
        sys.exit(0)
