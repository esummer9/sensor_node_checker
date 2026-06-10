import serial
import time
import binascii

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')

def test_raw_3():
    ser = serial.Serial('COM5', 9600, timeout=1)
    
    # 203 = 0x00CB, count = 2
    req = bytearray([0x04, 0x03, 0x00, 0xCB, 0x00, 0x02])
    req += calculate_crc(req)
    
    print(f"Sending: {binascii.hexlify(req)}")
    ser.write(req)
    time.sleep(0.5)
    response = ser.read(100)
    print(f"Received: {binascii.hexlify(response)}")

    ser.close()

if __name__ == "__main__":
    test_raw_3()
