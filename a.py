from pymodbus.client import ModbusSerialClient

# 1. 클라이언트 연결 설정
client = ModbusSerialClient(
    port='COM5', 
    baudrate=9600, 
    parity='E',             # PLC 설정과 맞출 것 (통상 E 또는 N)
    bytesize=8, stopbits=1, timeout=1
)

if client.connect():
    print("PLC와 연결 성공!")
    
    slave_id = 1  # PLC에 설정한 슬레이브 국번 (예: 1)

    # ---------------------------------------------------------
    # [1] PLC의 레지스터 값 읽기 (Read Holding Register - FC3)
    # ---------------------------------------------------------
    # 예: D0부터 D4까지 총 5개의 값을 읽어온다고 가정 (address=0이 D0에 맵핑된 경우)
    read_res = client.read_holding_registers(address=0, count=5, device_id=slave_id)
    
    if not read_res.isError():
        print(f"PLC D0~D4 읽기 완료: {read_res.registers}")
    else:
        print("읽기 실패!")

    # ---------------------------------------------------------
    # [2] PLC의 레지스터에 값 쓰기 (Write Holding Register - FC6 / FC16)
    # ---------------------------------------------------------
    # 예: D10 (address=10) 레지스터에 숫자 '999' 쓰기 (단일 쓰기)
    write_res = client.write_register(address=10, value=999, device_id=slave_id)
    
    if not write_res.isError():
        print("PLC D10 레지스터에 999 쓰기 성공!")
    else:
        print("쓰기 실패!")
        
    client.close()
else:
    print("포트 열기 실패")
