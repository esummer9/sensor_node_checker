import serial
import time
import binascii

def test_raw():
    ser = serial.Serial('COM5', 9600, timeout=2)
    # Request for Slave 4, Function 3 (Read Holding Regs), Address 203 (0x00CB), Count 1 (0x0001)
    # CRC for 04 03 00 cb 00 01 is f4 59
    request_fc3 = bytes([0x04, 0x03, 0x00, 0xCB, 0x00, 0x01, 0xF4, 0x59])
    
    print(f"Sending FC3: {binascii.hexlify(request_fc3)}")
    ser.write(request_fc3)
    time.sleep(0.5)
    response = ser.read(100)
    print(f"Received: {binascii.hexlify(response)}")
    
    # Request for Slave 4, Function 4 (Read Input Regs), Address 203 (0x00CB), Count 1 (0x0001)
    # CRC for 04 04 00 cb 00 01 is 45 99
    request_fc4 = bytes([0x04, 0x04, 0x00, 0xCB, 0x00, 0x01, 0x45, 0x99])
    
    print(f"\nSending FC4: {binascii.hexlify(request_fc4)}")
    ser.write(request_fc4)
    time.sleep(0.5)
    response = ser.read(100)
    print(f"Received: {binascii.hexlify(response)}")

    ser.close()

if __name__ == "__main__":
    test_raw()
