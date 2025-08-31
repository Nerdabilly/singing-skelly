import asyncio
import argparse
import threading
from bleak import BleakClient, BleakScanner
from queue import Queue

from ble_core import play_or_pause_file, WRITE_UUID, NOTIFY_UUID, handle_notification

BLE_DEVICE_ADDRESS = "81:58:8C:87:67:72"
command_queue = Queue()
ble_client = None

# =======================
# BLE Connection Thread
# =======================

async def ble_loop():
    global ble_client

    print("Scanning for device...")
    device = await BleakScanner.find_device_by_address(BLE_DEVICE_ADDRESS)
    if not device:
        print("Device not found.")
        return

    async with BleakClient(device) as client:
        ble_client = client
        print(f"Connected to {device.address}")

        await client.start_notify(NOTIFY_UUID, handle_notification)

        while True:
            if not command_queue.empty():
                cmd_bytes = command_queue.get()
                print(f"[SEND] {cmd_bytes.hex().upper()}")
                try:
                    await client.write_gatt_char(WRITE_UUID, cmd_bytes)
                except Exception as e:
                    print(f"Failed to send command: {e}")
            await asyncio.sleep(0.05)  # light wait loop

def start_ble_thread():
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=lambda: loop.run_until_complete(ble_loop()), daemon=True)
    t.start()
    return loop
