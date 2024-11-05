import asyncio
import cv2
import numpy as np
import mediapipe as mp
import logging
import threading
import time
from queue import Queue
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from aiortc import MediaStreamTrack
from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD

# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Parameters for robot movement
stepSize = 0.4
AXIS_THRESHOLD = 0.3

# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)

# Queue for receiving video frames
frame_queue = Queue()

async def execute_action(conn, action):
    """Executes the given action on the robot."""
    if action == 'forward':
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"],
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": stepSize, "y": 0, "z": 0, "mode": 4}}
        )
    elif action == 'backward':
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"],
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": -stepSize, "y": 0, "z": 0}}
        )
    elif action == 'left':
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"],
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": stepSize * 2}}
        )
    elif action == 'right':
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"],
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": -stepSize * 2}}
        )

async def recv_camera_stream(track: MediaStreamTrack):
    """Receives video frames from the robot and puts them in the frame queue."""
    while True:
        frame = await track.recv()
        img = frame.to_ndarray(format="bgr24")
        frame_queue.put(img)

def run_asyncio_loop(loop):
    """Runs the asyncio loop for robot connection in a separate thread."""
    asyncio.set_event_loop(loop)
    async def setup():
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="unitree.local")
        await conn.connect()

        # Enable video streaming
        conn.video.switchVideoChannel(True)
        conn.video.add_track_callback(recv_camera_stream)

    loop.run_until_complete(setup())
    loop.run_forever()

async def track_hand_and_control_robot(conn):
    """Tracks the hand in the video feed and controls the robot based on hand position."""
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = hand_landmarks.landmark
                    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP].y
                    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP].y

                    # Check if the hand is open
                    hand_open = (pinky_tip - thumb_tip) > 0.1

                    # Calculate hand position
                    hand_x = landmarks[mp_hands.HandLandmark.WRIST].x * frame.shape[1]
                    frame_center_x = frame.shape[1] / 2

                    if hand_open:
                        if hand_x < frame_center_x - 50:
                            await execute_action(conn, 'left')
                        elif hand_x > frame_center_x + 50:
                            await execute_action(conn, 'right')
                        else:
                            await execute_action(conn, 'forward')
                    else:
                        print("Hand not open, robot will not move.")

            # Display the video feed with MediaPipe annotations
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            # Sleep briefly to reduce CPU load
            await asyncio.sleep(0.01)

    cv2.destroyAllWindows()

async def main():
    # Initialize connection to the robot
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="unitree.local")
    await conn.connect()

    # Run the hand tracking and control loop
    await track_hand_and_control_robot(conn)

if __name__ == "__main__":
    # Setup asyncio loop in a separate thread for video handling
    loop = asyncio.new_event_loop()
    asyncio_thread = threading.Thread(target=run_asyncio_loop, args=(loop,))
    asyncio_thread.start()

    # Run the main hand tracking and control function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)
