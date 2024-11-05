import asyncio
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
import numpy as np
import struct

# Helperfunctie om numpy array om te zetten naar PointCloud2
def create_point_cloud_msg(positions):
    msg = PointCloud2()
    msg.header.frame_id = "map"  # Vervang door de correcte frame_id
    
    msg.height = 1
    msg.width = positions.shape[0]
    
    msg.fields = [
        PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
    ]
    msg.is_bigendian = False
    msg.point_step = 12  # 3 floats * 4 bytes each
    msg.row_step = msg.point_step * positions.shape[0]
    msg.is_dense = True
    
    # Maak de data aan in een bytestring
    msg.data = np.array(positions, dtype=np.float32).tobytes()
    
    return msg

class LidarPointCloudPublisher(Node):
    def __init__(self):
        super().__init__('lidar_point_cloud_publisher')
        self.publisher_ = self.create_publisher(PointCloud2, 'lidar/point_cloud', 10)

    def publish_point_cloud(self, positions):
        point_cloud_msg = create_point_cloud_msg(positions)
        self.publisher_.publish(point_cloud_msg)

async def main():
    # Initialize ROS2
    rclpy.init()

    node = LidarPointCloudPublisher()
    
    async def lidar_callback(message):
        data = message["data"]
        positions = data['data']['positions']
        positions = positions.reshape(-1, 3)
        
        # Publiceer de point cloud in ROS2-formaat
        node.publish_point_cloud(positions)

    # Maak verbinding met de LIDAR en verwerk de data zoals je eerder deed
    # Voeg hier de WebRTC logica toe, roep lidar_callback aan bij ontvangst van data
    # Abonneer op het juiste topic en hou de node draaiende
    
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
