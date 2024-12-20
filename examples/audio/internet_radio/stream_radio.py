import logging
import asyncio
import sys
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from aiortc.contrib.media import MediaPlayer
from go2_webrtc_driver.constants import RTC_TOPIC, VUI_COLOR


# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)

async def main():
    try:
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="unitree.local")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber="B42D2000XXXXXXXX")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.Remote, serialNumber="B42D2000XXXXXXXX", username="email@gmail.com", password="pass")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
        
        await conn.connect()


        # Set Volume to 50%
        print("Setting volume to 20% (2/10)...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["VUI"], 
            {
                "api_id": 1003,
                "parameter": {"volume": 2}
            }
        )


        stream_url = "https://nashe1.hostingradio.ru:80/ultra-128.mp3" #Radio ultra
        stream_url = "https://icecast.vrtcdn.be/mnm-high.mp3"
        

        logging.info(f"Playing internet radio: {stream_url}")
        player = MediaPlayer(stream_url)  # Use MediaPlayer with the URL
        audio_track = player.audio  # Get the audio track from the player
        conn.pc.addTrack(audio_track)  # Add the audio track to the WebRTC connection

        await asyncio.sleep(3600)  # Keep the program running to handle events

    except ValueError as e:
        logging.error(e)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C to exit gracefully.
        print("\nProgram interrupted by user")
        sys.exit(0)