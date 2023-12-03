import machine
import random
from machine import Pin, I2C
from i2c_lcd import I2cLcd
import time


SERVO_PIN = 15  # GPIO 14
ir_sensor_pin = Pin(14, Pin.IN)
# Create servo object
servo = machine.PWM(machine.Pin(SERVO_PIN), freq=50)
LCD_I2C_ADDR = 0x27
ROW_PINS = [16, 17, 18, 19]
COL_PINS = [21, 22, 23, 2]
KEYS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=10000)

lcd = I2cLcd(i2c, LCD_I2C_ADDR, 2, 16)
row_pins = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in ROW_PINS]
col_pins = [Pin(pin, Pin.OUT) for pin in COL_PINS]

# Create RFID object

def stop_servo():
    # Stop the servo motor
    servo.duty(0)
    
def unlock_door():
    # Rotate servo to unlock the door
    servo.duty(30)  # Adjust duty cycle based on your servo

def lock_door():
    # Rotate servo to lock the door
    servo.duty(120)  # Adjust duty cycle based on your servo
stop_servo()

def read_key():
    
    for i in range(len(COL_PINS)):
        col_pins[i].value(0)

        for j in range(len(ROW_PINS)):
            if row_pins[j].value() == 0:
                return KEYS[j][i]

        col_pins[i].value(1)
    return None
def detect_objects():
    while True:
        # Read the state of the IR sensor
        ir_state = ir_sensor_pin.value()

        # Check if an object is detected
        if ir_state == 0:
            print("Object detected!")
            return True
        else:
            print("No object detected.")

        # Add a delay to avoid continuous printing
        time.sleep(1)

#configure the ESP32 wifi as station mode
import network
sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
    print("Connecting to network...")
    sta.active(True)
    #sta.connect("your wifi ssid", "your wifi password")
    sta.connect("realme X7 Max","12345678")
    while not sta.isconnected():
        pass
print("Network Configuration:",sta.ifconfig())

#configure the socket connection over TCP/IP
import socket
#AF_INET - use Internet Protoccol v4 addresses
#SOCK_STREAM means that it is a TCP socket.
#SOCK_DGRAM means that is is a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#specifies that the socket is reachable by any address the machine happens to have
s.bind(('', 80))
#max of 5 socket connections
s.listen(5)
def gen():
    global retrieved_string
    characters = '0123456789ABCD'

    # Generate a random 8-character string
    random_string = ''.join(random.choice(characters) for _ in range(8))

    # Save the random string to a text file
    with open("random_string.txt", "w") as file:
        file.write(random_string)

    # Retrieve the random string from the text file
    with open("random_string.txt", "r") as file:
        retrieved_string = file.read()

    return retrieved_string
entered_keys = ""
#function for creating the web page to be displayed
def web_page():
    a=gen()
    html_page ="""
      <html>
      <head>
         <meta content = "width=device-width, initial-scale=1" name="viewport"></meta>
      </head>
      <body>
      <center><h2>Key Generation </h2></center>
      <center>
         <form action="/gen" method="get">
                <button type="submit" name="Generate" value="Gen">Generate</button>
         </form>
      </center>
      <center><p>Generated Number: <strong>"""+a+"""</strong>.</p></center>
      </body>
      </html>"""
    return html_page
while True:
    #Socket accept()
    conn, addr = s.accept()
    print("Got connection from %s"%str(addr))
    #Socket receive()
    request = conn.recv(1024)
    print("")
    print("")
    print("Content %s"%str(request))
    #Socket send()
    request = str(request)
    response = web_page()
    conn.send("HTTP/1.1 200 OK\n")
    conn.send("Content-Type: text/html\n")
    
    conn.send("Connection: close\n\n")
    conn.sendall(response)
    
    #Socket close()
    conn.close()
    if detect_objects()==True:
        lcd.putstr('Enter Passcode!')
        time.sleep(5)
        lcd.clear()
        while True:
            key = read_key()
            if key:
                print("Key pressed:", key)
                if key == '#':
                    print("Enter key pressed")
                    stored_digits = entered_keys
                    print("Stored Digits:", stored_digits)
                    if stored_digits == retrieved_string:
                        lcd.clear()
                        lcd.putstr("Access Granted")
                        time.sleep(2)
                        lcd.clear()
                        unlock_door()
                        time.sleep(5)
                        lock_door()
                    entered_keys = ""
                    web_page()
                    break

                elif key == '*':
                    print("Backspace key pressed")
                    entered_keys = entered_keys[:-1]  

                else:
                    entered_keys += key
                entered_keys = entered_keys[-8:]

                lcd.clear()

                lcd.move_to(0, 0)
                lcd.putstr(entered_keys)

                time.sleep(0.5)

            time.sleep(0.1
