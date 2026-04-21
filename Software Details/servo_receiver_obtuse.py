import network
import espnow
from machine import Pin, PWM
import time

# --- ESP-NOW Setup ---
# This ESP's MAC address (replace with your receiver's MAC if different)
# You can find this by running the sender code and looking at the 'receiver_esp' variable
sender_esp_mac = b'\xE0\x8C\xFE\x32\xB5\x48' # This should be the sender's MAC address

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

e = espnow.ESPNow()
e.active(True)

# --- Servo Setup ---
# Define servo pins. Adjust these to your actual servo connections.
# Assuming 4 servos for character movement.
servo_pin_1 = Pin(13) # Example pin for Servo 1
servo_pin_2 = Pin(12) # Example pin for Servo 2
servo_pin_3 = Pin(14) # Example pin for Servo 3
servo_pin_4 = Pin(27) # Example pin for Servo 4

servo_1 = PWM(servo_pin_1, freq=50)
servo_2 = PWM(servo_pin_2, freq=50)
servo_3 = PWM(servo_pin_3, freq=50)
servo_4 = PWM(servo_pin_4, freq=50)

# Servo pulse width values (adjust these for your specific servos)
# Duty cycle for ESP32 PWM is 0-1023. A 50Hz signal has a period of 20ms.
# 1ms pulse = (1/20) * 1024 = 51.2
# 1.5ms pulse = (1.5/20) * 1024 = 76.8
# 2ms pulse = (2/20) * 1024 = 102.4

# These are example duty cycle values. You will likely need to fine-tune them.
# A common range for 0-180 degrees is 20-120 (or similar) out of 1024.
DUTY_MIN = 20  # Corresponds to 0 degrees
DUTY_MAX = 120 # Corresponds to 180 degrees

# Angles for character movement (obtuse angles)
CENTER_ANGLE = 90
OBTUSE_ANGLE_LEFT = 120 # Example obtuse angle for left movement
OBTUSE_ANGLE_RIGHT = 120 # Example obtuse angle for right movement

def angle_to_duty(angle):
    # Map angle (0-180) to duty cycle (DUTY_MIN-DUTY_MAX)
    return int((angle / 180) * (DUTY_MAX - DUTY_MIN) + DUTY_MIN)

def set_servo_angle(servo_pwm, angle):
    duty = angle_to_duty(angle)
    servo_pwm.duty(duty)

# --- Global variable to store received button states ---
# [up_button, down_button, left_button, right_button]
# 0 = pressed, 1 = released (from sender's perspective, active low)
received_button_raw_states = [1, 1, 1, 1] 

def espnow_recv_cb(espnow_obj):
    host, msg = espnow_obj.irecv(0)  # Non-blocking
    if msg:
        try:
            global received_button_raw_states
            data_str = msg.decode('utf-8')
            # Sender sends: up.value(), down.value(), left.value(), right.value()
            # These are 0 when pressed, 1 when released
            up_val, down_val, left_val, right_val = map(int, data_str.split(','))
            
            received_button_raw_states = [up_val, down_val, left_val, right_val]
            # print(
Received:
Received:", data_str, "-> Raw States:", received_button_raw_states)
        except ValueError:
            print("Received malformed data:", msg)

e.irq(espnow_recv_cb)

print("Receiver ready. Waiting for button inputs...")

# Initialize all servos to center position
set_servo_angle(servo_1, CENTER_ANGLE)
set_servo_angle(servo_2, CENTER_ANGLE)
set_servo_angle(servo_3, CENTER_ANGLE)
set_servo_angle(servo_4, CENTER_ANGLE)

while True:
    up_pressed    = (received_button_raw_states[0] == 0)
    down_pressed  = (received_button_raw_states[1] == 0)
    left_pressed  = (received_button_raw_states[2] == 0)
    right_pressed = (received_button_raw_states[3] == 0)

    # --- Servo Control Logic ---
    # When left is clicked, servo 1 and 3 move (alternate, same direction)
    if left_pressed and not right_pressed:
        set_servo_angle(servo_1, OBTUSE_ANGLE_LEFT) # Move servo 1 to obtuse angle
        set_servo_angle(servo_3, OBTUSE_ANGLE_LEFT) # Move servo 3 to obtuse angle
        set_servo_angle(servo_2, CENTER_ANGLE) # Reset other servos
        set_servo_angle(servo_4, CENTER_ANGLE)
    # When right is clicked, servo 2 and 4 move (alternate, same direction)
    elif right_pressed and not left_pressed:
        set_servo_angle(servo_2, OBTUSE_ANGLE_RIGHT) # Move servo 2 to obtuse angle
        set_servo_angle(servo_4, OBTUSE_ANGLE_RIGHT) # Move servo 4 to obtuse angle
        set_servo_angle(servo_1, CENTER_ANGLE) # Reset other servos
        set_servo_angle(servo_3, CENTER_ANGLE)
    else:
        # If no left/right is pressed, return all servos to center
        set_servo_angle(servo_1, CENTER_ANGLE)
        set_servo_angle(servo_2, CENTER_ANGLE)
        set_servo_angle(servo_3, CENTER_ANGLE)
        set_servo_angle(servo_4, CENTER_ANGLE)

    # Up and Down buttons can be used for other movements if desired, or ignored
    # For now, they don't affect the servos based on the current request.

    time.sleep(0.05) # Small delay to prevent busy-waiting and allow ESP-NOW to process
