import asyncio
import socket
import json
from bleak import BleakClient, BleakScanner
from ble_core import (
    ble_send_cmd,
    handle_notification,
    play_or_pause_file,
    query_file_info,
    NOTIFY_UUID,
    BLE_DEVICE_ADDRESS
)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765


async def handle_command(client, cmd_dict):
    cmd = cmd_dict.get("command")

    if cmd == "playpause":
        print("playpause received")
        serial = int(cmd_dict.get("serial"))
        action = int(cmd_dict.get("action"))
        cmd_bytes = play_or_pause_file(serial, action)
        await ble_send_cmd(client, cmd_bytes)
        return {"status": "sent", "serial": serial, "action": action}

    elif cmd == "query_file_info":
        cmd_bytes = query_file_info()
        result = await ble_send_cmd(client, cmd_bytes, response_key="file_info")
        return {"status": "ok", "file_info": result}

    return {"error": "Unknown command"}

async def handle_client(reader, writer):
    try:
        data = await reader.read(1024)
        cmd_dict = json.loads(data.decode())
        result = await handle_command(writer.client, cmd_dict)
    except Exception as e:
        result = {"error": str(e)}

    writer.write(json.dumps(result).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def command_server(client):
    print(f"[BLE] Listening on {SERVER_HOST}:{SERVER_PORT}")

    async def client_handler(reader, writer):
        # Attach the BLE client to the writer so it can be accessed in handle_client
        writer.client = client
        await handle_client(reader, writer)

    server = await asyncio.start_server(client_handler, SERVER_HOST, SERVER_PORT)

    async with server:
        await server.serve_forever()

async def main():
    print("🔍 Scanning for BLE device...")
    device = await BleakScanner.find_device_by_address(BLE_DEVICE_ADDRESS)

    if not device:
        print("❌ BLE device not found.")
        return

    async with BleakClient(device) as client:
        print(f"✅ Connected to {device.address}")
        await client.start_notify(NOTIFY_UUID, handle_notification)

        # 🟢 This should keep the program running (assuming it handles CLI requests)
        await command_server(client)


    

# async def main():
#     print("🔍 Scanning for BLE device...")
#     device = await BleakScanner.find_device_by_address(BLE_DEVICE_ADDRESS)

#     if not device:
#         print("❌ BLE device not found.")
#         return

#     async with BleakClient(device) as client:
#         print(f"✅ Connected to {device.address}")
#         await client.start_notify(NOTIFY_UUID, handle_notification)
#         await command_server(client)
    
#     loop = asyncio.get_event_loop()
#     loop.create_task(poll_file_info_loop())

if __name__ == "__main__":
    asyncio.run(main())
