from pymodbus.client import ModbusSerialClient

# ... [시리얼 연결 설정] ...
client = ModbusSerialClient(
    port='COM5', 
    baudrate=9600, 
    parity='N',            # 짝수(Even) 패리티 설정 추가! ('N'=None, 'E'=Even, 'O'=Odd)
    # bytesize=8,            # 데이터 비트
    stopbits=1,            # 스탑 비트
    timeout=1,
    handle_local_echo=True  # 이 옵션을 추가해보세요!
)

try:
    client.connect()

    start_address = 1 # 레지스터 주소 1에 접근하기 위해 offset 0 사용 (기기에 따라 1일 수 있음)
    count = 8 # 1번부터 8번까지 총 8개의 레지스터 읽기

    for slave_id in range(1,1+1):
        # 레지스터 읽기 (FX5U PLC의 경우 일반적으로 Holding Register인 FC3를 사용합니다)
        try:
            response = client.read_holding_registers(address=start_address, count=count, device_id=slave_id)

            if response.isError():
                print(f"읽기 에러 발생: {response}")
            else:
                regs = getattr(response, 'registers', [])
                print(f"응답 원본: {response}")
                print(f"수신된 레지스터 데이터: {regs}")
                
                if not regs or len(regs) < 8:
                    print(f"에러: 기기에서 충분한 레지스터 데이터를 보내지 않았습니다. (데이터가 비어있거나 부족함) device_id={slave_id}")
                    print(f"💡 힌트 1: 레지스터 주소가 잘못되었을 수 있습니다. start_address를 {1 if start_address == 0 else 0}로 변경해보세요.")
                else:
                    # 레지스터 데이터 파싱
                    agency_code = regs[0]      # 주소 1
                    company_code = regs[1]     # 주소 2
                    product_type = regs[2]     # 주소 3
                    product_code = regs[3]     # 주소 4
                    protocol_version = regs[4] # 주소 5
                    channel_count = regs[5]    # 주소 6
                    
                    # 시리얼 번호는 uint32이므로 주소 7(regs[6])과 주소 8(regs[7])을 합쳐야 함
                    # (엔디안 설정에 따라 regs[6] << 16 | regs[7] 또는 그 반대일 수 있습니다)
                    serial_number = (regs[6] << 16) + regs[7] 

                    print("=== 양액기 노드 정보 ===")
                    print(f"기관코드: {agency_code}")
                    print(f"회사코드: {company_code}")
                    print(f"제품타입: {product_type}")
                    print(f"제품코드: {product_code}")
                    print(f"프로토콜버전: {protocol_version}")
                    print(f"채널수: {channel_count}")
                    print(f"시리얼번호: {serial_number}")
        except Exception as e:
            print(f"[{slave_id}번 국번] 통신 예외 발생 (응답 없음): {e}", end='\n\n')
except Exception as e:
    print("예외 발생 : " + str(e))
finally:
    client.close()