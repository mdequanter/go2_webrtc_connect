import asyncio
import logging
import sys
import json
import numpy as np
import zlib
import open3d as o3d
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod

# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)

# Function to decompress voxel map and convert to numpy array
def decompress_voxel_data(voxel_data_compressed):
    try:
        # Decompress the data using zlib
        decompressed_bytes = zlib.decompress(voxel_data_compressed)
        # Convert to JSON and load as a Python dictionary
        decompressed_str = decompressed_bytes.decode('utf-8')
        voxel_dict = json.loads(decompressed_str)
        return voxel_dict
    except Exception as e:
        logging.error(f"Failed to decompress voxel data: {e}")
        return None

# Function to convert voxel data to Open3D point cloud
def voxel_data_to_point_cloud(voxel_data):
    try:
        positions = voxel_data.get('positions', [])
        if not positions:
            logging.warning("No voxel positions found in the data.")
            return None
        # Convert positions to numpy array
        voxel_positions_np = np.array(positions, dtype=np.float32)
        # Create Open3D point cloud
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(voxel_positions_np)
        return point_cloud
    except Exception as e:
        logging.error(f"Failed to convert voxel data to point cloud: {e}")
        return None

# Function to visualize voxel data
def visualize_voxel_data(point_cloud):
    try:
        if point_cloud is not None:
            o3d.visualization.draw_geometries([point_cloud])
        else:
            logging.warning("Cannot visualize empty point cloud.")
    except Exception as e:
        logging.error(f"Failed to visualize point cloud: {e}")

# Callback function to handle LIDAR voxel map messages
def lidar_callback(message):
    try:
        # Print the received message for debugging purposes
        #print("Received LIDAR message:", message)
        lidar_data = message
        # Extract and decompress voxel map data
        voxel_data = lidar_data
        point_cloud = voxel_data_to_point_cloud(voxel_data)
        print (point_cloud)
        # Visualize the point cloud
        visualize_voxel_data(point_cloud)

    except Exception as e:
        logging.error(f"Error in LIDAR callback: {e}")

# Main async function to connect to WebRTC and handle LIDAR messages
async def main():
    try:
        # Choose a connection method (uncomment the correct one)
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="192.168.0.56")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber="B42D2000XXXXXXXX")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.Remote, serialNumber="B42D2000XXXXXXXX", username="email@gmail.com", password="pass")
        #conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)

        # Connect to the WebRTC service.
        await conn.connect()

        # Disable traffic saving mode on the data channel.
        await conn.datachannel.disableTrafficSaving(True)

        # Publish a message to turn the LIDAR sensor on.
        conn.datachannel.pub_sub.publish_without_callback("rt/utlidar/switch", "on")

        # Subscribe to the LIDAR voxel map data and use the callback function to process incoming messages.
        conn.datachannel.pub_sub.subscribe("rt/utlidar/voxel_map_compressed", lidar_callback)

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
