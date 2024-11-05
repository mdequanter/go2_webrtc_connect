import asyncio
import logging
import json
import sys
import pygame
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD
import time

# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)

stepSize = 0.4
brightness_level = 0
EulerPos = True
EulerX = 0.0
EulerY = 0.0
EulerZ = 0.0

StandoutMode = False

# Joystick drempel voor detectie van beweging
AXIS_THRESHOLD = 0.3

async def execute_action(conn, action):
    """Executes the given action on the robot."""
    global brightness_level, EulerPos, EulerX, EulerY, EulerZ,StandoutMode,brightness_level
    if action == 'forward':
        print("Moving forward...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": stepSize, "y": 0, "z": 0, "mode" : 4}}
        )
    elif action == 'backward':
        print("Moving backward...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": -stepSize, "y": 0, "z": 0}}
        )
    elif action == 'left':
        print("Moving left...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": stepSize*2}}
        )
    elif action == 'right':
        print("Moving right...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": -stepSize*2}}
        )
    elif action == 'stepleft':
        print("step left...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": stepSize, "z": 0}}
        )
    elif action == 'stepright':
        print("step right...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": -stepSize, "z": 0}}
        )
    elif action == 'pose_x':
        print(f"Adjusting EulerX pose to {EulerX}...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Euler"], "parameter": {"x": EulerX, "y": EulerY, "z": EulerZ}}
        )
    elif action == 'pose_y':
        print(f"Adjusting EulerY pose to {EulerY}...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Euler"], "parameter": {"x": EulerX, "y": EulerY, "z": EulerZ}}
        )
    elif action == 'standup':
        print("Switching to StandUp Mode...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["RecoveryStand"], "parameter": {"data": False}}
        )
    elif action == 'stretch':
        print("Stretching...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Stretch"], "parameter": {"data": False}}
        )
    elif action == 'wiggle':
        print("Wiggling...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["WiggleHips"], "parameter": {"data": False}}
        )
    elif action == 'hello':
        print("Performing Hello gesture...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Hello"]}
        )
    elif action == 'sit':
        print("Performing Sit gesture...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Sit"]}
        )
    elif action == 'down':
        print("Performing Damp...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["StandDown"]}
        )
    elif action == 'StandOut':
        print("Performing StandOut...")
        if (StandoutMode == False) :
            newMode =  True
        else :
            newMode = False
        await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {
                    "api_id": SPORT_CMD["StandOut"],
                    "parameter": {"data": newMode}
                }
            )
        await asyncio.sleep(5)

        await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {
                    "api_id": SPORT_CMD["StandOut"],
                    "parameter": {"data": False}
                }
            )
        await asyncio.sleep(5)

    elif action == 'light':
        brightness_level = 10 if brightness_level == 0 else 0
        print(f"Setting light brightness to {brightness_level}...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["VUI"], 
            {"api_id": 1005, "parameter": {"brightness": brightness_level}}
        )
        print(f"Brightness level: {brightness_level}/10")
        await asyncio.sleep(0.5)
    elif action == 'ai':
        print("Switching motion mode to 'AI'...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"], 
            {
                "api_id": 1002,
                "parameter": {"name": "ai"}
            }
        )
        await asyncio.sleep(10)
    elif action == 'normal':
        print("Switching motion mode to 'Normal mode'...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"], 
            {
                "api_id": 1002,
                "parameter": {"name": "normal"}
            }
        )
        await asyncio.sleep(10)



async def main():
    global EulerX,EulerY,EulerZ,EulerPos
    # Initialize connection
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="unitree.local")
    await conn.connect()

    pygame.init()
    screen = pygame.display.set_mode((400, 450))
    pygame.display.set_caption("Robot Control with Gamepad")

    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Connected to joystick: {joystick.get_name()}")

    previous_hats = [(0, 0)] * joystick.get_numhats()

    asyncio.create_task(execute_action(conn, 'normal'))

    '''
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["SPORT_MOD"], 
        {
            "api_id": 1011,
            "parameter": {"data": 3}
        }
    )
    '''

    running = True
    while running:
        screen.fill((30, 30, 30))
        pygame.display.flip()  # Update display

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Joystick as-invoer uitlezen
        if joystick:
            axis_0 = joystick.get_axis(0)  # Left-right movement
            axis_1 = joystick.get_axis(1)  # Forward-backward movement
            axis_3 = joystick.get_axis(3)  # Pose X adjustment
            axis_4 = joystick.get_axis(4)  # Pose Y adjustment

            if (joystick.get_button(0) == 1) : # button X
                print ("Wiggling")
                asyncio.create_task(execute_action(conn, 'wiggle'))
            if (joystick.get_button(3) == 1) : # button square
                print ("Stretch")
                asyncio.create_task(execute_action(conn, 'stretch'))
            if (joystick.get_button(1) == 1) : # button circle
                print ("Hello")
                asyncio.create_task(execute_action(conn, 'hello'))
            if (joystick.get_button(2) == 1) : # button Triangle
                print ("Sit")
                asyncio.create_task(execute_action(conn, 'sit'))
            if (joystick.get_button(6) == 1) : # button Triangle
                print ("Standup")
                asyncio.create_task(execute_action(conn, 'standup'))
            if (joystick.get_button(7) == 1) : # button Triangle
                print ("Standup")
                print ("Down")
                asyncio.create_task(execute_action(conn, 'down'))
            if (joystick.get_button(8) == 1) : # button king
                print ("Switch to AI")
                asyncio.create_task(execute_action(conn, 'ai'))
            if (joystick.get_button(9) == 1) : # button king
                print ("Switch to AI")
                asyncio.create_task(execute_action(conn, 'normal'))
            if (joystick.get_button(10) == 1) : # button king
                print ("Perform Standout")
                asyncio.create_task(execute_action(conn, 'StandOut'))
            if (joystick.get_button(4) == 1) : # button king
                print ("Control Light")
                asyncio.create_task(execute_action(conn, 'light'))
                await asyncio.sleep(0.5)
        



            if (EulerPos == True and (abs(axis_1) > AXIS_THRESHOLD or abs(axis_0) > AXIS_THRESHOLD)) :
                await conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], 
                    {"api_id": SPORT_CMD["RecoveryStand"], "parameter": {"data": False}}
                )
                EulerPos = False
                await asyncio.sleep(0.5)
            hat = joystick.get_hat(0)
            if hat != previous_hats[0]:  # Alleen toon veranderingen
                print(f"hat waarde: {hat}")
                if (hat[0] == -1):
                    asyncio.create_task(execute_action(conn, 'stepleft'))
                if (hat[0] == 1):
                    asyncio.create_task(execute_action(conn, 'stepright'))
                previous_hats[0] = hat

            # Check beweging assen voor de joystick
            if abs(axis_1) > AXIS_THRESHOLD:
                if axis_1 < 0:
                    asyncio.create_task(execute_action(conn, 'forward'))
                elif axis_1 > 0:
                    asyncio.create_task(execute_action(conn, 'backward'))
            if abs(axis_0) > AXIS_THRESHOLD:
                if axis_0 < 0:
                    asyncio.create_task(execute_action(conn, 'left'))
                elif axis_0 > 0:
                    asyncio.create_task(execute_action(conn, 'right'))

            if (EulerPos == False and (abs(axis_3) > AXIS_THRESHOLD or abs(axis_4) > AXIS_THRESHOLD)) :
                await conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], 
                    {"api_id": SPORT_CMD["RecoveryStand"], "parameter": {"data": False}}
                )
                EulerPos = False
                await asyncio.sleep(0.5)


            # Check pose assen (Euler modus)
            if abs(axis_3) > AXIS_THRESHOLD:
                EulerPos = True
                EulerX += 0.1 if axis_3 > 0 else -0.1
                EulerX = max(-0.75, min(0.75, EulerX))  # Clamp waarde
                asyncio.create_task(execute_action(conn, 'pose_x'))

            if abs(axis_4) > AXIS_THRESHOLD:
                EulerPos = True
                EulerY += 0.1 if axis_4 > 0 else -0.1
                EulerY = max(-0.75, min(0.75, EulerY))  # Clamp waarde
                asyncio.create_task(execute_action(conn, 'pose_y'))


        await asyncio.sleep(0.1)  # Kleine pauze om CPU-belasting te verminderen

    pygame.quit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)
