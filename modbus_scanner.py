from pymodbus.client import ModbusSerialClient
import time

# 1. 시리얼 통신 설정 (본인의 환경에 맞게 수정 필요)
# port: 장치 관리자에서 확인한 COM 포트 (예: 'COM5')
# baudrate, parity, bytesize, stopbits는 PLC/슬레이브 장치 설정과 정확히 일치해야 합니다.
client = ModbusSerialClient(
    port='COM5',
    baudrate=9600,
    parity='N',
    bytesize=8,
    stopbits=1,
    timeout=1
)

def read_plc_registers():
    # 2. 연결 시도
    if not client.connect():
        print("시리얼 포트 연결에 실패했습니다. 포트 번호와 설정을 확인하세요.")
        return

    print("시리얼 포트에 연결되었습니다.")

    # 3. 데이터 읽기 설정
    start_address = 0
    count = 300  # 0부터 300까지이므로 총 301개
    try:
        # 1번부터 9번까지 스캔
        for slave_id in [4]:
            time.sleep(1)
            registers_to_read = [203, 212, 230, 233, 239]
            print(f"\n\n--- slave_id : {slave_id} ---")
            try:
                for reg in registers_to_read:
                    response = client.read_holding_registers(
                        address=reg, 
                        count=1, 
                        device_id=slave_id
                    )
                    if response.isError():
                        print(f"Address {reg}: 에러 발생 - {response}")
                    else:
                        print(f"Address {reg}: {response.registers[0]}")
            except Exception as e:
                print(f"기기 {slave_id}번 통신 예외 발생: {e}")

    finally:
        # 5. 연결 종료
        client.close()
        print("연결이 종료되었습니다.")

if __name__ == "__main__":
    read_plc_registers()