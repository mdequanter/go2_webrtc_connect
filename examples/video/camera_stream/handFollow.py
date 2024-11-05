import cv2
import numpy as np

# Create an OpenCV window and display a blank image
height, width = 720, 1280  # Adjust the size as needed
img = np.zeros((height, width, 3), dtype=np.uint8)
cv2.imshow('Video', img)
cv2.waitKey(1)  # Ensure the window is created

import asyncio
import logging
import threading
import time
import sys
from queue import Queue
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from aiortc import MediaStreamTrack
from go2_webrtc_driver.constants import RTC_TOPIC, VUI_COLOR, SPORT_CMD
import mediapipe as mp


# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils


# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)

stepSize = 0.1




def main():
    frame_queue = Queue()

    # Choose a connection method (uncomment the correct one)
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="unitree.local")
    # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber="B42D2000XXXXXXXX")
    # conn = Go2WebRTCConnection(WebRTCConnectionMethod.Remote, serialNumber="B42D2000XXXXXXXX", username="email@gmail.com", password="pass")
    #conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)

    # Async function to receive video frames and put them in the queue
    async def recv_camera_stream(track: MediaStreamTrack):
        while True:
            frame = await track.recv()
            # Convert the frame to a NumPy array
            img = frame.to_ndarray(format="bgr24")
            frame_queue.put(img)

    def execute_action(conn, action):
        if action == 'left':
            print("Moving left...")
            conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": stepSize*2}}
            )
            time.sleep(0.5)
        elif action == 'right':
            print("Moving right...")
            conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": -stepSize*2}}
            )


    def run_asyncio_loop(loop):
        asyncio.set_event_loop(loop)
        async def setup():
            try:
                # Connect to the device
                await conn.connect()

                brightness_level = 10

                await conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["VUI"], 
                    {
                        "api_id": 1005,
                        "parameter": {"brightness": brightness_level}
                    }
                )
                print(f"Brightness level: {brightness_level}/10")
                await asyncio.sleep(0.5)



                # Switch video channel on and start receiving video frames
                conn.video.switchVideoChannel(True)

                # Add callback to handle received video frames
                conn.video.add_track_callback(recv_camera_stream)
            except Exception as e:
                logging.error(f"Error in WebRTC connection: {e}")

        # Run the setup coroutine and then start the event loop
        loop.run_until_complete(setup())
        loop.run_forever()

    # Create a new event loop for the asyncio code
    loop = asyncio.new_event_loop()

    # Start the asyncio event loop in a separate thread
    asyncio_thread = threading.Thread(target=run_asyncio_loop, args=(loop,))
    asyncio_thread.start()

    try:
        while True:
            if not frame_queue.empty():
                img = frame_queue.get()
                frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        landmarks = hand_landmarks.landmark
                        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP].y
                        pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP].y
                        mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        # Check if the hand is open
                        hand_open = (pinky_tip - thumb_tip) > 0.1

                        # Calculate hand position
                        hand_x = landmarks[mp_hands.HandLandmark.WRIST].x * img.shape[1]
                        frame_center_x = img.shape[1] / 2

                        if hand_open:
                            if hand_x < frame_center_x - 50:
                                print("Moving left...")
                                execute_action(conn, 'left')
                                #await execute_action(conn, 'left')
                            elif hand_x > frame_center_x + 50:
                                print("Moving right...")
                                #asyncio.create_task(execute_action(conn, 'left'))
                            else:
                                print ("forward")
                                #await execute_action(conn, 'forward')
                        else:
                            print ("not open")
                            #print("Hand not open, robot will not move.")
                
                #print(f"Shape: {img.shape}, Dimensions: {img.ndim}, Type: {img.dtype}, Size: {img.size}")
                # Display the frame
                cv2.imshow('Video', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # Sleep briefly to prevent high CPU usage
                time.sleep(0.01)
    finally:
        cv2.destroyAllWindows()
        # Stop the asyncio event loop
        loop.call_soon_threadsafe(loop.stop)
        asyncio_thread.join()

if __name__ == "__main__":
    main()
