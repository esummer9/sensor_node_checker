import serial
import time
import binascii

def test_listen():
    ser = serial.Serial('COM3', 9600, timeout=1)
    print("Listening on COM5 for 15 seconds...")
    start = time.time()
    while time.time() - start < 15:
        data = ser.read(100)
        if data:
            print(f"[{time.time()-start:.2f}s] Received: {binascii.hexlify(data)}")

    ser.close()

if __name__ == "__main__":
    test_listen()
