import cv2
import numpy as np
import serial
from simple_pid import PID
arduino = serial.Serial(port='COM3', baudrate=115200, timeout=1) 
import time

PIDpoint = [90, 90]
cx = 0

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    time.sleep(2)

    # print('panjang frame:', frame.shape[1])
    low_b = np.uint8([38,38,38])
    high_b = np.uint8([0,0,0])
    mask = cv2.inRange(frame, high_b, low_b)
    contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
    if len(contours) > 0 :
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] !=0 :
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            # print("CX : "+str(cx)+"  CY : "+str(cy))
            # if cx >= 120 :
            #     print("Turn Left")
            # if cx < 120 and cx > 40 :
            #     print("On Track!")
            # if cx <=40 :
            #     print("Turn Right")
            cv2.circle(frame, (cx,cy), 5, (255,255,255), -1)
    else :
        # print("I don't see the line")
        cx = int(frame.shape[1]/2)
    
    setpointx = cx

    def pidcontrolx(errorx):
        pidx = PID(0.5, 0.2, 0.01, setpointx, sample_time=0.01, output_limits=(-25, 25)) #satu fungsi hanya berlaku untuk 1 error, tidak bisa multi
        koreksix = pidx(errorx)
        if errorx == setpointx:
            evaluasi = errorx + koreksix #disinlah letak pengurangan error oleh koreksi
        else:
            evaluasi = errorx + koreksix
        return evaluasi
    PIDpointupdate = pidcontrolx(PIDpoint[len(PIDpoint)-1])
    PIDpoint.append(PIDpointupdate)
    PIDsumbux = PIDpoint[len(PIDpoint)-1]
    # if cx == int(frame.shape[1]/2):
    #     print(int(PIDsumbux), 'lurus')
    # elif cx < int(frame.shape[1]/2): 
    #     print(int(PIDsumbux), 'kiri')
    # elif cx > int(frame.shape[1]/2): 
    #     print(int(PIDsumbux), 'kanan')

    visualtitikpeyimpanganPID1 = (int(frame.shape[1]/2), int(100))
    visualtitikpeyimpanganPID2 = (int(PIDsumbux), int(100))
    visualtitikpeyimpangan1 = (int(int(frame.shape[1]/2)), int(100))
    visualtitikpeyimpangan2 = (int(cx), int(100))

    if PIDsumbux >= frame.shape[1]:
        PIDsumbux = PIDsumbux - frame.shape[1]
        servo = (160*PIDsumbux)/frame.shape[1]
        servo = int(0-servo)
    elif PIDsumbux < frame.shape[1]:
        PIDsumbux = frame.shape[1] - PIDsumbux
        servo = (160*PIDsumbux)/frame.shape[1]
        servo = int(0+servo)
    servo = servo - 80
    servo = str(servo)
    arduino.write(bytes(str.encode(servo)))
    print(servo, ' servo ', PIDsumbux, )

    cv2.line(frame, visualtitikpeyimpanganPID1, visualtitikpeyimpanganPID2, (0,255,0), thickness=3 )
    cv2.line(frame, visualtitikpeyimpangan1, visualtitikpeyimpangan2, (0,255,255), thickness=1 )

    # cv2.drawContours(frame, c, -1, (0,255,0), 1)
    cv2.imshow("Mask",mask)
    cv2.imshow("Frame",frame)
    if cv2.waitKey(1) & 0xff == ord('q'):   # 1 is the time in ms
        break
cap.release()
cv2.destroyAllWindows()