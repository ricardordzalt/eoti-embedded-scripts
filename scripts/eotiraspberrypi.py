import asyncio
import cv2
import socketio
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceServer,
    RTCConfiguration,
    RTCIceCandidate,
    MediaStreamTrack,
    VideoStreamTrack,
)
from aiortc.contrib.media import PlayerStreamTrack, MediaPlayer
import numpy as np
import av
from fractions import Fraction
from picamera2 import Picamera2

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Configuración del servidor de señalización
SIGNALING_SERVER = 'https://eoti-server.onrender.com'
stun_server = RTCIceServer(urls='stun:stun.l.google.com:19302')
config = RTCConfiguration(iceServers=[stun_server])

## VideoTrack class to capture camera with picamera2
class VideoTrack(VideoStreamTrack):
    kind = 'video'

    def __init__(self):
        super().__init__()

        self.video_capture = Picamera2()
        # self.video_capture.configure(self.video_capture.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        self.video_capture.start()
        self.pts = 0  # Inicializar el valor de pts
        self.time_base = Fraction(1, 30)  # Establecer time_base según el FPS deseado

    async def recv(self):
        try:
            # Capture a frame from the video
            img = self.video_capture.capture_array()
            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(grey, 1.1, 5)
            if(len(faces) > 0):
                print(len(faces), "face/s detected, this data can be send by socket")
            color_img = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)  # Convertir imagen en escala de grises a BGR
            # Create a new VideoFrame
            new_frame = av.VideoFrame.from_ndarray(color_img)
            new_frame.pts = self.pts
            new_frame.time_base = self.time_base
            self.pts += 1  # Incrementar el valor de pts para el siguiente cuadro

            # Return the VideoFrame
            return new_frame

        except Exception as e:
            # Código para manejar cualquier otra excepción
            print("Ocurrió un error:", str(e))



async def run():
    # Inicializar el socketio
    sio = socketio.AsyncClient()
    auth = { 'userId': '00:1A:2B:3C:4D:5E' }
    # Conectar al servidor de señalización
    await sio.connect(SIGNALING_SERVER, auth=auth)


    # Crear una nueva conexión de pares
    pc = None

    # # Crear una nueva conexión de pares
    # pc = RTCPeerConnection(configuration=config)


    @sio.event
    async def newCall(data):
        nonlocal pc
        print("newcall")


        rtcMessage = data['rtcMessage']
        # Crear la descripción de la sesión remota
        remote_desc = RTCSessionDescription(sdp=rtcMessage['sdp'], type=rtcMessage['type'])


        # Cerrar la conexión WebRTC anterior (si existe)
        await close_connection()


        # Crear un nuevo RTCPeerConnection
        pc = RTCPeerConnection(configuration=config)
        video_sender = pc.addTrack(video_track)
        video_sender.direction = "sendonly"


        # Establecer la descripción de la sesión remota
        await pc.setRemoteDescription(remote_desc)


        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        @pc.on("icecandidate")
        async def on_icecandidate(event):
            print("event ice")
            candidate = event.candidate
            if candidate:
                # Enviar el candidato ICE al servidor de señalización
                response = {
                    'userId': 'webrtc1',
                    'rtcMessage': {
                        'candidate': candidate.candidate,
                        'sdpMid': candidate.sdpMid,
                        'sdpMLineIndex': candidate.sdpMLineIndex
                    }
                }
                await sio.emit('ICEcandidate', response)


        response = {'userId': 'webrtc1', 'rtcMessage': {'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type} }
        await sio.emit('answerCall', response)

    @sio.event
    async def ICEcandidate(data):
        # rtcMessage = data['rtcMessage']
        candidate = data['rtcMessage']
        # candidate = RTCIceCandidate(rtcMessage['candidate'], rtcMessage['sdpMid'], rtcMessage['sdpMLineIndex'])
        await pc.addIceCandidate(candidate)

    # Evento de conexión exitosa con el servidor
    @sio.event
    def connect():
        print('Conexión establecida con el servidor')
        # Aquí puedes ejecutar la lógica adicional cuando te conectas al servidor
        # ...

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("1connectionstatechange", pc.connectionState)

    @pc.on("signalingstatechange")
    async def on_connectionstatechange():
        print("2signalingstatechange", pc.iceConnectionState)

    @pc.on("icecandidateerror")
    async def on_connectionstatechange():
        print("3signalingstatechange", pc.iceGatheringState)


    @pc.on("track")
    async def on_track(event):
        print("event", event)
        # while true:
        #     frame = await event.recv()
        #     print("frame", frame)
        #     img = frame.to_ndarray(format="bgr24")
            #     cv2.imshow("Stream", img)
            #     if cv2.waitKey(1) == 27:  # Presiona Esc para salir
            #         break
        # cv2.destroyAllWindows()
        
    async def close_connection():
        nonlocal pc
        if pc:
            # Cerrar la conexión RTCPeerConnection
            pc.close()
            await pc.wait_closed()
            pc = None

    await sio.wait()

# Ejecutar el programa
if __name__ == '__main__':
    # asyncio.ensure_future(recv_track())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("error")
        pass
    finally:
        loop.close()
