import asyncio
import logging
import json
import sys
import pygame
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD

# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)

stepSize = 0.4
brightness_level = 0
EulerPos = False
EulerX =  0.0
EulerY = 0.0
EulerZ = 0.0

# Define a mapping between pygame keys and actions
key_action_map = {
    pygame.K_UP: 'forward',
    pygame.K_DOWN: 'backward',
    pygame.K_a: 'left',
    pygame.K_e: 'right',
    pygame.K_RIGHT: 'turnright',
    pygame.K_LEFT: 'turnleft',
    pygame.K_r: 'standup',
    pygame.K_t: 'stretch',
    pygame.K_i: 'wiggle',
    pygame.K_y: 'hello',
    pygame.K_o: 'sit',  
    pygame.K_u: 'down', 
    pygame.K_l: 'light',
    pygame.K_m: 'euler'

}

# Define the button layout and actions
buttons = [
    ("Forward", "forward", (150, 50)),
    ("Backward", "backward", (150, 150)),
    ("Left", "left", (50, 100)),
    ("Right", "right", (250, 100)),
    ("Turn Left", "turnleft", (50, 50)),
    ("Turn Right", "turnright", (250, 50)),
    ("Stand Up", "standup", (50, 250)),
    ("Stretch", "stretch", (150, 250)),
    ("Hello", "hello", (250, 250)),
    ("Sit", "sit", (50, 300)),
    ("Euler", "euler", (50, 350)),
    ("Wiggle", "wiggle", (150, 300)),
    ("Down", "down", (250, 300)),
    ("Light", "light", (150, 350))
]

class Button:
    def __init__(self, text, action, pos, size=(80, 40)):
        self.text = text
        self.action = action
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.color = (100, 100, 250)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 24)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

async def execute_action(conn, action):
    """Executes the given action on the robot."""
    global brightness_level, EulerPos, EulerX, EulerY, EulerZ
    if action == 'euler':
        if (EulerPos == True) :
            print("Enter walking mode...")
            EulerPos = False
            EulerX =  0.0
            EulerY = 0.0
            EulerZ = 0.0            
        else :
            EulerPos = True
            print("Enter Euler mode...")
        
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {"api_id": SPORT_CMD["Euler"], "parameter": {"x": 0.0, "y": 0.0, "z": 0.0}}
        )
    if action == 'forward':
        print("Moving forward...")
        if (EulerPos == False) :
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": stepSize, "y": 0, "z": 0}}
                )
        else :
            print(" set Euler pose...")
            EulerY = EulerY + 0.1
            if (EulerY >= 0.75) : 
                EulerY = 0.75            
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Euler"], "parameter": {"x": EulerX, "y": EulerY, "z": EulerZ}}
            )
    
            

    elif action == 'backward':
        print("Moving Bckward...")
        if (EulerPos == False) :
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": -stepSize, "y": 0, "z": 0}}
                )
        else :
            print(" set Euler pose...")
            EulerY = EulerY - 0.2
            if (EulerY <= -0.75) : 
                EulerY = -0.75              
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Euler"], "parameter": {"x": EulerX, "y": EulerY, "z": EulerZ}}
            )
    elif action == 'left':
        print("Moving left...")
        if (EulerPos == False) :
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": stepSize, "z": 0}}
                )
        else :
            print(" set Euler pose...")
            EulerX = EulerX - 0.2
            if (EulerX < -0.75) : 
                EulerX = -0.75
            print(f" set EulerX pose ({EulerX})...")

            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Euler"], "parameter": {"x": EulerX, "y": EulerY, "z": EulerZ}}
            )
    elif action == 'right':
        print("Moving right...")
        if (EulerPos == False) :
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": -stepSize, "z": 0}}
                )
        else :
            
            EulerX = EulerX + 0.2
            if (EulerX > 0.75) : 
                EulerX = 0.75
            print(f" set EulerX pose ({EulerX})...")
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Euler"], "parameter": {"x": EulerX, "y": EulerY, "z": EulerZ}}
            )
    elif action == 'turnleft':
        print("Turning left...")
        if (EulerPos == False) :
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": stepSize*2}}
                )
        else :
            print(" set Euler pose...")
            EulerZ = EulerZ - 0.2
            if (EulerZ <= -0.6) : 
                EulerZ = -0.6               
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Euler"], "parameter": {"x": EulerX, "y": EulerY, "z": EulerZ}}
            )
    elif action == 'turnright':
        
        print("Turning right...")
        if (EulerPos == False) :
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": -stepSize*2}}
                )
        else :
            print(" set Euler pose...")
            EulerZ = EulerZ + 0.2
            if (EulerZ >= 0.6) : 
                EulerZ = 0.6   
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
    elif action == 'light':
        print(f"Setting light brightness to {brightness_level}...")
        brightness_level = 10 if brightness_level == 0 else 0
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["VUI"], 
            {"api_id": 1005, "parameter": {"brightness": brightness_level}}
        )
        print(f"Brightness level: {brightness_level}/10")
        await asyncio.sleep(0.5)

async def main():
    # Initialize connection
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="unitree.local")
    await conn.connect()

    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["VUI"], 
        {"api_id": 1005, "parameter": {"brightness": 0}}
    )

    '''
    # Switch to Normal mode
    print("Switching motion mode to 'Normal'...")
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["MOTION_SWITCHER"], 
        {
            "api_id": 1002,
            "parameter": {"name": "normal"}
        }
    )
    await asyncio.sleep(10)
    '''

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 450))
    pygame.display.set_caption("Robot Control")

    # Create button objects
    button_objects = [Button(text, action, pos) for text, action, pos in buttons]

    print("Press keys to control the robot or click buttons.")

    # Main event loop
    running = True
    while running:
        screen.fill((30, 30, 30))  # Clear screen with a dark background

        # Draw buttons
        for button in button_objects:
            button.draw(screen)

        pygame.display.flip()  # Update display

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in key_action_map:
                    action = key_action_map[event.key]
                    asyncio.create_task(execute_action(conn, action))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for button in button_objects:
                    if button.is_clicked(mouse_pos):
                        asyncio.create_task(execute_action(conn, button.action))

        await asyncio.sleep(0.01)  # Small delay to yield control

    pygame.quit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)
