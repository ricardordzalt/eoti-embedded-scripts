import asyncio
import json
import socketio
import subprocess
import time

from collections import OrderedDict
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.rtcrtpparameters import RTCRtpCodecCapability
from pitrack import H264EncodedStreamTrack

codec_parameters = OrderedDict(
    [
        ("packetization-mode", "1"),
        ("level-asymmetry-allowed", "1"),
        ("profile-level-id", "42001f"),
    ]
)

pi_capability = RTCRtpCodecCapability(
    mimeType="video/H264", clockRate=90000, channels=None, parameters=codec_parameters
)

preferences = [pi_capability]

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

encoder = H264Encoder(10000000)

picam2.start_recording(encoder, 'test.h264')
# time.sleep(10)
# picam2.stop_recording()

# Crear una instancia de SocketIO
sio = socketio.AsyncClient()


def get_mac_address():
    # Obtener la dirección MAC del dispositivo Linux
    result = subprocess.run(["ifconfig", "-a"], capture_output=True, text=True)
    ifconfig_output = result.stdout
    # Analizar la salida de ifconfig para encontrar la dirección MAC
    mac_address = None
    for line in ifconfig_output.splitlines():
        if "ether" in line:
            mac_address = line.strip().split(" ")[1]
            break
    return mac_address


@sio.event
async def newCall(data):
    rtcMessage = data['rtcMessage']
    rtc_sdp = rtcMessage['sdp']
    rtc_type = rtcMessage['type']
    # Crear una instancia de RTCPeerConnection
    pc = RTCPeerConnection()
    userId = data['userId']
    # Configura el evento onicecandidate para manejar los candidatos ICE
    @pc.on("ICEcandidate")
    async def on_icecandidate(candidate):
      if candidate:
        # Envía el candidato ICE al cliente remoto
        await sio.emit('ICEcandidate', {
            'userId': userId,
            'rtcMessage': candidate.to_sdp()
        })

    # Establecer la descripción remota
    offer = RTCSessionDescription(sdp=rtc_sdp, type=rtc_type)
    await pc.setRemoteDescription(offer)

    for t in pc.getTransceivers():
      print(t)
      # if t.kind == "audio" and audio and audio.audio:
      #   pc.addTrack(audio.audio)
      if t.kind == "video" and video_track:
        print("video")
        t.setCodecPreferences(preferences)
        pc.addTrack(encoder)

    video_track = H264EncodedStreamTrack(30)
    pc.addTrack(video_track)

    # Crear una respuesta
    answer = await pc.createAnswer()

    # Establecer la descripción local
    await pc.setLocalDescription(answer)
    response = {
      'rtcMessage': {
          'sdp': pc.localDescription.sdp,
          'type': pc.localDescription.type
      },
      'userId': userId
    }
    await sio.emit('answerCall', response)


async def main():
    auth_data = {
        'userId': get_mac_address()
    }
    # Conectar al servidor socketio
    await sio.connect('http://192.168.100.7:3000', auth=auth_data)
    await sio.wait()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
