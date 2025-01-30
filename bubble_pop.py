import cv2
import random
from cvzone.HandTrackingModule import HandDetector

#webcam int.
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

detector = HandDetector(detectionCon=0.7, maxHands=1)

class Bubble:
    def __init__(self, x, y, speed, radius=20):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.color = (255, 255, 255)  # White

    def move(self):
        self.y += self.speed

    def draw(self, frame):
        cv2.circle(frame, (self.x, self.y), self.radius, self.color, 2)


# initial vals.
bubbles = []
score = 0
missed = 0
frame_count = 0
game_over = False

# Quit button
quit_button_x, quit_button_y = 540, 10
quit_button_width, quit_button_height = 90, 40

def is_quit_button_clicked(mouse_x, mouse_y):
    return quit_button_x <= mouse_x <= quit_button_x + quit_button_width and \
           quit_button_y <= mouse_y <= quit_button_y + quit_button_height

# detect quit button click
def mouse_callback(event, x, y, flags, param):
    global game_over
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        if is_quit_button_clicked(x, y):
            game_over = True

cv2.namedWindow("Pop the Bubble")
cv2.setMouseCallback("Pop the Bubble", mouse_callback)

try:
    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Unable to access the camera.")
            break

        frame = cv2.flip(frame, 1)
        frame_count += 1

        # Detect hands
        hands, frame = detector.findHands(frame, flipType=False)

        
        if frame_count % 30 == 0:  #every 30 frames
            x_pos = random.randint(50, 590)
            speed = random.randint(5, 10)  #speed
            bubbles.append(Bubble(x_pos, 0, speed))

        for bubble in bubbles[:]:
            bubble.move()
            bubble.draw(frame)
            if bubble.y > 480:
                bubbles.remove(bubble)
                missed += 1

        
        if hands:
            lm_list = hands[0]['lmList']
            finger_tip = lm_list[8]
            finger_x, finger_y = finger_tip[0], finger_tip[1]

        
            for bubble in bubbles[:]:
                distance = ((finger_x - bubble.x) ** 2 + (finger_y - bubble.y) ** 2) ** 0.5
                if distance < bubble.radius:
                    bubbles.remove(bubble)
                    score += 1

        cv2.putText(frame, f"Score: {score}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Missed: {missed}/5", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.rectangle(frame, (quit_button_x, quit_button_y),
                      (quit_button_x + quit_button_width, quit_button_y + quit_button_height),
                      (0, 0, 0), -1)
        cv2.putText(frame, "QUIT", (quit_button_x + 10, quit_button_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2)

        if missed >= 5:
            game_over = True
            break

        cv2.imshow("Pop the Bubble", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if game_over:
            break

    # Game over screen
    if game_over:
        while True:
            cv2.putText(frame, "GAME OVER", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv2.putText(frame, f"Final Score: {score}", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow("Pop the Bubble", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except Exception as e:
    print(f"An error occurred: {e}")

cap.release()
cv2.destroyAllWindows()
