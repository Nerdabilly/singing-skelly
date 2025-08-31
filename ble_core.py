from bleak import BleakClient
import asyncio
import requests
import json 
from pprint import pprint

WRITE_UUID = "0000ae01-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000ae02-0000-1000-8000-00805f9b34fb"
last_playing_state = None  # True or False
# Shared variable to hold future for responses
response_futures = {}

last_param_sent = None

def int_to_hex(n: int, byte_len: int):
    return hex(n)[2:].zfill(byte_len * 2).upper()

def crc8(data: bytes) -> str:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc >> 1) ^ 0x8C) if (crc & 1) else (crc >> 1)
    return f"{crc:02X}"



def build_cmd(tag: str, payload: str = "00") -> bytes:
    base_str = "AA" + tag + payload
    if len(payload) < 16:
        base_str += "0" * (16 - len(payload))
    crc = crc8(bytes.fromhex(base_str))
    return bytes.fromhex(base_str + crc)

def play_or_pause_file(serial: int, action: int):
    global last_param_sent
    # send param to device
    last_param_sent = action
    cmd = build_cmd("C6", int_to_hex(serial, 2) + int_to_hex(action, 1))
    print( " ***************  PLAY COMMAND SENT ***************** ")
    print(cmd)
    return cmd

def query_file_info():
    return build_cmd("D0")

async def ble_send_cmd(client: BleakClient, cmd_bytes: bytes, response_key: str = None):
    if response_key:
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        response_futures[response_key] = future
    await client.write_gatt_char(WRITE_UUID, cmd_bytes)
    if response_key:
        return await asyncio.wait_for(response_futures[response_key], timeout=5)


def handle_notification(sender, data):
    hexstr = data.hex().upper()
    print(f"[BLE] handle_notification hexstr: {hexstr}")

 
    global last_param_sent
 


    if hexstr.startswith("BBD0"):

        file_index = int(hexstr[4:8], 16)
        cluster = int(hexstr[8:16], 16)
        total_files = int(hexstr[16:20], 16)
        attr = int(hexstr[24:26], 16)
        eye_icon = int(hexstr[110:112], 16)
        db_pos = int(hexstr[112:114], 16)
        file_info = {
            "index": file_index,
            "cluster": cluster,
            "total": total_files,
            "attr": attr,
            "eye_icon": eye_icon,
            "db_pos": db_pos
        }

        fut = response_futures.pop("file_info", None)
        if fut and not fut.done():
            fut.set_result(file_info)
    
    if hexstr.startswith("BBC6"):
        #print(f"[BBD0] Received {hexstr}")
        playing = last_param_sent == 1  # <== 1 = playing, 0 = paused?
        #print(f"[BBD0] Playing? {playing}")
        if last_param_sent is None or last_param_sent != playing:
            state = "PLAYING" if playing else "PAUSED"
            #print(f"[INFO] Playback state changed: {state}")

        serial = int(hexstr[4:8], 16)
        #playing = int(hexstr[8:10], 16) 
        duration = int(hexstr[10:14], 16)

        is_playing = (bool(playing))
        state = "▶️ Playing" if is_playing else "⏸️ Paused"

        print(f"[BLE] Serial {serial}: {state} (duration: {duration} sec)")
        if is_playing:
            print(f"Skelly reports file {serial} is playing, sending RESUME command to player")
            try:
                response = requests.put( 'http://127.0.0.1:8001/v1/player/resume')
                    
                             
                print("http request normally here")
                print(f"[HTTP] PUT status: {response.status_code} Reason: {response.reason}")
                print(f"[HTTP] PUT status: {response.url}")
                print(f"[HTTP] Headers: {response.headers}")
                
             

                pprint(vars(response.request))
            except requests.exceptions.RequestException as e:
                print(f"[HTTP ERROR] {e}")

        return
