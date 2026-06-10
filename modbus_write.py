from pymodbus.client import ModbusSerialClient

# 1. Modbus RTU 설정 (환경에 맞게 포트 수정)
client = ModbusSerialClient(
    port='COM5',          # 시리얼 포트
    baudrate=9600,        # KS X 3288 표준 기반 통신 속도
    parity='N',
    stopbits=1,
    bytesize=8
)

def start_irrigation(slave_id, zone_number, duration_minutes):
    """
    KS X 3288 표준 관수 제어 (가상의 표준 레지스터 매핑)
    - zone_number: 1 ~ 6
    - duration_minutes: 60
    """
    # [참고] 표준 문서의 특정 레지스터 주소(Address)를 사용해야 합니다.
    # 아래 주소는 표준 예시이며, 실제 양액기 매뉴얼의 'Modbus Map'을 확인하세요.
    REG_START_BASE = 0x1000  # 관수 시작 명령 레지스터 시작 주소
    REG_TIME_BASE = 0x2000   # 관수 시간 설정 레지스터 시작 주소

    if not client.connect():
        print("연결 실패")
        return

    # 1. 관수 시간 설정 (60분)
    result = client.write_register(REG_TIME_BASE + (zone_number - 1), duration_minutes, device_id=slave_id)
    print('result1', result)
    
    # 1. 성공 여부 확인
    # 2. 관수 시작 신호 (1을 쓰면 시작)
    result = client.write_register(REG_START_BASE + (zone_number - 1), 1, device_id=slave_id)
    print('result2', result)
    print(f"구역 {zone_number}: {duration_minutes}분 관수 시작 명령 전송 완료")

# 2. 1번부터 6번 구역까지 반복 수행
if __name__ == "__main__":
    for zone in range(1, 7):
        start_irrigation(slave_id=1, zone_number=zone, duration_minutes=60)
    
    client.close()