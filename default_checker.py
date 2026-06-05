import serial
import time

def calculate_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')

def scan_ksx3266_node(port_name, baudrate=9600):
    print(f"포트 {port_name}에서 KS X 3266 (Modbus RTU) 센서 국번 스캔을 시작합니다...")
    print("스캔 범위: 1 ~ 247 (응답 대기로 인해 약 15~20초 소요됩니다)")
    try:
        ser = serial.Serial(port_name, baudrate, timeout=0.15) 
    except Exception as e:
        print(f"포트 연결 오류: {e}")
        return

    try:
        found_ids = []
        
        # 모드버스 국번 1번부터 247번까지 스캔
        for node_id in range(1, 248):
            # KS X 3267 규격은 주로 입력 레지스터(0x04)를 사용하여 센서값을 읽습니다.
            # 시작번지(0x0000)부터 1개의 데이터(0x0001) 읽기 요청
            req = bytearray([node_id, 0x04, 0x00, 0x00, 0x00, 0x01])
            req += calculate_crc(req)
            
            ser.reset_input_buffer()
            ser.write(req)
            if node_id < 15:
                time.sleep(0.3)
            else :
                time.sleep(0.15)
            
            if ser.in_waiting > 0:
                resp = ser.read(ser.in_waiting)
                # 정상적인 모드버스 RTU 응답인지 확인 (SlaveID, Function Code 일치 및 길이)
                if len(resp) >= 5 and resp[0] == node_id and resp[1] == 0x04:
                    # CRC 검증
                    if calculate_crc(resp[:-2]) == resp[-2:]:
                        print(f"\n[성공] 센서 국번(Node ID) 찾음: {node_id}")
                        found_ids.append(node_id)
                        break
            
            # 진행 상황 표시
            if node_id % 10 == 0:
                print(".", end="", flush=True)
    
        print("\n")
        if not found_ids:
            print("응답하는 센서 노드를 찾지 못했습니다. 결선, 전원, 통신 속도(Baudrate)를 확인해주세요.")
        else:
            print(f"스캔 완료. 연결된 센서 국번 목록: {found_ids}")
    finally:
        ser.close()

if __name__ == '__main__':
    # 장치관리자에서 확인한 COM 포트로 변경해주세요 (예: COM3)
    scan_ksx3266_node('COM3', 9600)