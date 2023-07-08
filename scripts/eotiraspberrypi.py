import asyncio
import cv2
import socketio
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
    RTCIceServer,
    RTCConfiguration,
    RTCIceCandidate,
    MediaStreamTrack,
)
from aiortc.contrib.media import PlayerStreamTrack, MediaPlayer
import numpy as np
        
# Configuración del servidor de señalización
SIGNALING_SERVER = 'http://192.168.100.8:3000'
stun_server = RTCIceServer(urls='stun:stun.l.google.com:19302')
config = RTCConfiguration(iceServers=[stun_server])

class VideoFrame:
    def __init__(self, width, height, data):
        self.width = width
        self.height = height
        self.data = data

    def to_ndarray(self):
        return np.frombuffer(self.data, np.uint8).reshape((self.height, self.width, 3))

    @staticmethod
    def from_ndarray(ndarray, format="bgr24"):
        height, width, channels = ndarray.shape
        if format == "bgr24":
            data = ndarray.tobytes()
        elif format == "rgb24":
            data = cv2.cvtColor(ndarray, cv2.COLOR_RGB2BGR).tobytes()
        else:
            raise ValueError(f"Unsupported format: {format}")

        return VideoFrame(width, height, data)

class VideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.video_capture = cv2.VideoCapture(0)  # Capturar el stream de la cámara, reemplaza 0 por el número de dispositivo adecuado si no es la cámara predeterminada

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        # Read the next frame using cv2.VideoCapture.read()
        ret, img = self.video_capture.read()
        print("recv1")
        if ret:
            # Convert the image to the desired format
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Create a new VideoFrame
            new_frame = VideoFrame.from_ndarray(img, format="rgb24")
            new_frame.pts = pts
            new_frame.time_base = time_base

            # # Show the captured frame using cv2.imshow()
            # cv2.imshow("Captured Frame", img)
            # cv2.waitKey(1)
            return new_frame
        else:
            # Video ended, close the connection
            return None


async def run():
    # Inicializar el socketio
    sio = socketio.AsyncClient()
    auth = { 'userId': 'webrtc2' }
    # Conectar al servidor de señalización
    await sio.connect(SIGNALING_SERVER, auth=auth)

    # Crear una nueva conexión de pares
    pc = RTCPeerConnection(configuration=config)
        video_track = VideoTrack()
        pc.addTrack(video_track)  # Agrega la pista de video al objeto RTCPeerConnection

    @sio.event
    async def newCall(data):
        print("newcall")
        rtcMessage = data['rtcMessage']
        # Crear la descripción de la sesión remota
        remote_desc = RTCSessionDescription(sdp=rtcMessage['sdp'], type=rtcMessage['type'])
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
        rtcMessage = data['rtcMessage']
        candidate = RTCIceCandidate(rtcMessage['candidate'], rtcMessage['sdpMid'], rtcMessage['sdpMLineIndex'])
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
        print("Receiving video track...")
        while True:
            frame = await event.recv()
            img = frame.to_ndarray(format="bgr24")
            cv2.imshow("Stream", img)
            if cv2.waitKey(1) == 27:  # Presiona Esc para salir
                break
        cv2.destroyAllWindows()


    await sio.wait()

# async def recv_track():
#     print("recv_Track")

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

