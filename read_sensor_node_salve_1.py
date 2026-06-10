import asyncio
import logging
import struct
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

PORT = 'COM3'
BAUDRATE = 9600

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ─── float 디코딩 함수 (안전한 방식) ───
def decode_float_safe(client, registers):
    """
    다양한 디코딩 방식을 시도하여 float 값을 안전하게 변환합니다.
    """
    try:
        # CDAB (Little Endian Word) -> 해당 센서의 정확한 통신 규격
        val_cdab = client.convert_from_registers(registers, data_type=client.DATATYPE.FLOAT32, word_order='little')
        if isinstance(val_cdab, list) and len(val_cdab) > 0: val_cdab = float(val_cdab[0])
        elif isinstance(val_cdab, (int, float)): val_cdab = float(val_cdab)

        return val_cdab
    except Exception as e:
        logging.debug(f"convert_from_registers failed: {e}. Trying manual fallback.")
        try:
            high_word, low_word = registers[0], registers[1]
            combined_cdab = (low_word << 16) | high_word
            val_cdab = struct.unpack('>f', struct.pack('>I', combined_cdab))[0]
            return val_cdab
        except Exception as e3:
            logging.error(f"Manual decoding also failed: {e3}")
            raise

# ─── 센서 단일 항목 비동기 처리 ───
async def read_sensor_async(modbus_client, slave_id, name, addr, cnt):
    """
    하나의 센서 값을 비동기적으로 읽습니다.
    블로킹 I/O를 'asyncio.to_thread'로 감싸 이벤트 루프를 방해하지 않습니다.
    """
    def read_and_decode():
        try:
            # 덤프 결과 확인: 센서 데이터가 0x04가 아닌 0x03(Holding Registers)에 저장되어 있습니다!
            rr = modbus_client.read_holding_registers(address=addr, count=cnt, device_id=slave_id)
            if rr.isError():
                logging.error(f"❌ {name} 레지스터 읽기 실패 (Slave {slave_id}): {rr}")
                return name, "Error"

            # 안전한 방식으로 float 디코딩 (CDAB)
            val = decode_float_safe(modbus_client, rr.registers)
            return name, round(val, 3)
        except ModbusIOException as e:
            logging.error(f"❌ {name} 통신 실패 (Slave {slave_id}): {e}")
            return name, "Read Error"
        except Exception as e:
            logging.error(f"❌ {name} 디코딩 실패 (Slave {slave_id}): {e}")
            return name, "Decode Error"

    return await asyncio.to_thread(read_and_decode)

async def main():
    # 덤프 결과 확인: qModMaster와 마찬가지로 오프셋 없이 원시 주소(203 등)를 그대로 사용합니다.
    targets = {
        "Outside Temperature": (203, 2),
        "Outside Humidity": (212, 2),
        "Wind Speed": (230, 2),
        "Wind Direction": (233, 2),
        "Outside CO2": (239, 2)
    }

    print(f"Connecting to {PORT}...")
    
    # pymodbus의 Serial Client 생성
    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        timeout=0.5,
        parity='N',
        stopbits=1,
        bytesize=8
    )
    
    if not client.connect():
        print(f"Failed to connect to {PORT}")
        return
    
    slavids = [1]

    for slave_id in slavids:
        print(f"\n--- Reading from Slave ID {slave_id} ---")
        for name, (addr, count) in targets.items():
            # 비동기 함수 호출 시 반드시 await 를 사용해야 합니다.
            result_name, value = await read_sensor_async(client, slave_id, name, addr, count)
            print(f"[{result_name}] Reg {addr}: Value={value}")
                
    client.close()

if __name__ == '__main__':
    # 비동기 main 함수 실행
    asyncio.run(main())
