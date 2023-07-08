import cv2

# Crea un objeto VideoCapture para acceder a la cámara
cap = cv2.VideoCapture(0)

while True:
    # Lee el siguiente fotograma de la cámara
    ret, frame = cap.read()
    print("ret",ret)
    print("frame", frame)
    if ret:
        # Muestra el fotograma en una ventana llamada "Video"
        cv2.imshow("Video", frame)

    # Espera 1 milisegundo y verifica si se presiona la tecla 'q' para salir del bucle
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera el objeto VideoCapture y cierra la ventana
cap.release()
cv2.destroyAllWindows()
