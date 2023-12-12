import cv2
import mediapipe as mp
import serial
import time
import serial.tools.list_ports
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
available_ports = [port.device for port in serial.tools.list_ports.comports()]
print("Available COM ports:", available_ports)
if available_ports:
    selected_port = available_ports[0]
else:
    print("No available COM ports found. Please check your Arduino connection.")
    exit()
try:
    arduino = serial.Serial(selected_port, 9600)
    print(f"Serial port {selected_port} opened successfully.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")


    
    exit()
cap = cv2.VideoCapture(0)
previous_finger_states = None
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            finger_states = [0, 0, 0, 0, 0]
            if len(hand_landmarks.landmark) >= 21:
                if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                    finger_states[0] = 1
                for i, (finger_tip, finger_base) in enumerate(zip([8, 12, 16, 20], [5, 9, 13, 17])):
                    if finger_tip < len(hand_landmarks.landmark) and finger_base < len(hand_landmarks.landmark):
                        if hand_landmarks.landmark[finger_tip].y < hand_landmarks.landmark[finger_base].y:
                            finger_states[i + 1] = 1
                current_finger_states_str = ''.join(map(str, finger_states)) + '*'
                if current_finger_states_str != previous_finger_states:
                    print(current_finger_states_str)
                    try:
                        arduino.write(current_finger_states_str.encode())
                        arduino.flush()
                    except Exception as e:
                        print(f"Error writing to Arduino: {e}")
                previous_finger_states = current_finger_states_str
            for lm in hand_landmarks.landmark:
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
arduino.close()