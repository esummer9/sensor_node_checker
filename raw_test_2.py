import serial
import time
import binascii

def test_raw_2():
    ser = serial.Serial('COM5', 9600, timeout=1)
    
    requests = [
        b'\x01\x03\x00\x00\x00\x01\x84\x0a', # ID 1
        b'\x02\x03\x00\x00\x00\x01\x84\x39', # ID 2
        b'\x04\x03\x00\x00\x00\x01\x84\x5f'  # ID 4
    ]
    
    for req in requests:
        print(f"\nSending: {binascii.hexlify(req)}")
        ser.write(req)
        time.sleep(0.5)
        response = ser.read(100)
        print(f"Received: {binascii.hexlify(response)}")

    ser.close()

if __name__ == "__main__":
    test_raw_2()
