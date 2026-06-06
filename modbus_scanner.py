from pymodbus.client import ModbusSerialClient
import time

# 1. 시리얼 통신 설정 (본인의 환경에 맞게 수정 필요)
# port: 장치 관리자에서 확인한 COM 포트 (예: 'COM5')
# baudrate, parity, bytesize, stopbits는 PLC/슬레이브 장치 설정과 정확히 일치해야 합니다.
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

client = None

def read_plc_registers():
    registers_to_read = [203, 212, 230, 233, 239]
    slave_id = 4

    for baudrate in [4800, 9600, 19200]:
        print(f"\n=============================================")
        print(f"Baudrate {baudrate} 테스트 중...")
        global client
        client = ModbusSerialClient(
            port='COM5',
            baudrate=baudrate,
            parity='N',
            bytesize=8,
            stopbits=1,
            timeout=1
        )
        if not client.connect():
            print(f"COM5 포트 열기 실패")
            continue

        try:
            # 1. Holding Registers 테스트
            print("  [Holding Registers (FC 3) 테스트]")
            for reg in registers_to_read:
                response = client.read_holding_registers(reg, 1, device_id=slave_id)
                if response.isError():
                    pass
                elif hasattr(response, 'registers') and response.registers:
                    print(f"    -> 성공! Address {reg}: {response.registers[0]}")
            
            # 2. Input Registers 테스트
            print("  [Input Registers (FC 4) 테스트]")
            for reg in registers_to_read:
                response = client.read_input_registers(reg, 1, device_id=slave_id)
                if response.isError():
                    pass
                elif hasattr(response, 'registers') and response.registers:
                    print(f"    -> 성공! Address {reg}: {response.registers[0]}")

        except Exception as e:
            print(f"  예외 발생: {e}")
        finally:
            client.close()

if __name__ == "__main__":
    read_plc_registers()