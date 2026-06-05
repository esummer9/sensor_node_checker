import serial
import struct
import time

PORT = 'COM3'
BAUDRATE = 9600

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

def read_registers(ser, slave_id, func_code, start_addr, count):
    req = bytearray([
        slave_id, func_code,
        (start_addr >> 8) & 0xFF, start_addr & 0xFF,
        (count >> 8) & 0xFF, count & 0xFF,
    ])
    req += calculate_crc(req)
    ser.reset_input_buffer()
    ser.write(req)
    time.sleep(0.3)
    if ser.in_waiting == 0:
        return None
    resp = ser.read(ser.in_waiting)
    expected_len = 3 + 2 * count + 2
    if len(resp) < expected_len:
        return None
    if resp[0] != slave_id or resp[1] != func_code:
        return None
    if calculate_crc(resp[:-2]) != resp[-2:]:
        return None
    byte_count = resp[2]
    data = resp[3:3 + byte_count]
    regs = []
    for i in range(0, len(data), 2):
        regs.append(int.from_bytes(data[i:i+2], byteorder='big'))
    return regs

def decode_float(regs):
    if len(regs) != 2:
        return None
    # Big Endian (ABCD) -> Pymodbus default
    combined = (regs[0] << 16) | regs[1]
    
    # Little Endian word, Big Endian byte (CDAB) -> BinaryPayloadDecoder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
    combined_cdab = (regs[1] << 16) | regs[0]
    
    try:
        val_abcd = struct.unpack('>f', struct.pack('>I', combined))[0]
    except:
        val_abcd = None
        
    try:
        val_cdab = struct.unpack('>f', struct.pack('>I', combined_cdab))[0]
    except:
        val_cdab = None
        
    return val_abcd, val_cdab

def main():
    targets = {
        "Outside Temperature": (203, 2),
        "Outside Humidity": (212, 2),
        "Wind Speed": (230, 2),
        "Wind Direction": (233, 2),
        "Outside CO2": (239, 2)
    }

    print(f"Connecting to {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=0.5)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    for slave_id in [1]:
        print(f"\n--- Reading from Slave ID {slave_id} ---")
        for name, (addr, count) in targets.items():
            regs = read_registers(ser, slave_id, 0x03, addr, count)
            if regs:
                val_abcd, val_cdab = decode_float(regs)
                abcd_str = f"{val_abcd:.3f}" if val_abcd is not None else "N/A"
                cdab_str = f"{val_cdab:.3f}" if val_cdab is not None else "N/A"
                print(f"[{name}] Reg {addr}: Raw={regs} | Float(ABCD)={abcd_str} | Float(CDAB)={cdab_str}")
            else:
                print(f"[{name}] Reg {addr}: Read Failed or No Response")
                
    ser.close()

if __name__ == '__main__':
    main()
