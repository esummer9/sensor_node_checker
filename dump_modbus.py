import asyncio
from pymodbus.client import ModbusSerialClient

PORT = 'COM3'
BAUDRATE = 9600
SLAVE_ID = 1

def main():
    print(f"Connecting to {PORT}...")
    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        timeout=1.0,
        parity='N',
        stopbits=1,
        bytesize=8
    )
    
    if not client.connect():
        print("Failed to connect.")
        return

    print(f"\n--- [1] 0x03 Holding Registers 스캔 (주소 200 ~ 250) ---")
    rr = client.read_holding_registers(address=200, count=50, device_id=SLAVE_ID)
    if not rr.isError():
        regs = rr.registers
        for i in range(0, len(regs)):
            addr = 200 + i
            if regs[i] != 0:
                print(f"Holding Reg {addr}: {regs[i]} (Hex: 0x{regs[i]:04X})")
    else:
        print("Error reading Holding Registers:", rr)

    print(f"\n--- [2] 0x04 Input Registers 스캔 (주소 200 ~ 250) ---")
    rr2 = client.read_input_registers(address=200, count=50, device_id=SLAVE_ID)
    if not rr2.isError():
        regs2 = rr2.registers
        for i in range(0, len(regs2)):
            addr = 200 + i
            if regs2[i] != 0:
                print(f"Input Reg {addr}: {regs2[i]} (Hex: 0x{regs2[i]:04X})")
    else:
        print("Error reading Input Registers:", rr2)

    client.close()

if __name__ == '__main__':
    main()
