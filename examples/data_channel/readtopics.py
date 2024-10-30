import asyncio
import logging
import sys
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
import numpy as np
import json

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

        def pose_callback(message):
            # Print de data ontvangen van de LIDAR-sensor.
            x = message['data']['pose']['position']['x']
            y = message['data']['pose']['position']['y']
            w = message['data']['pose']['orientation']['w']
            print (f"x: {x},  y: {y}, w: {w}")
  

        # Definieer een callback-functie om LIDAR-berichten te verwerken wanneer deze worden ontvangen.
        def data_callback(message):
            print (message)

        # Abonneer op de LIDAR voxel map data en gebruik de callback-functie om inkomende berichten te verwerken.
        #conn.datachannel.pub_sub.subscribe("rt/programming_actuator/command", data_callback)
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
