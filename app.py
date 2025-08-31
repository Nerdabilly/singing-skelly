from flask import Flask, request, jsonify
import asyncio
import threading
from bleak import BleakClient, BleakScanner

from comm_test import (
    WRITE_UUID, NOTIFY_UUID, BLE_DEVICE_ADDRESS,
    build_cmd, handle_notification, query_volume, play, pause, play_or_pause_file, query_file_info
)

app = Flask(__name__)

# Global BLE client and loop storage
ble_state = {
    "loop": None,
    "client": None,
    "device_address": BLE_DEVICE_ADDRESS,
}
loop_ready = threading.Event()

file_info_future = None

# ---------- Background Asyncio Loop ----------
def run_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ble_state["loop"] = loop
    loop_ready.set()
    loop.run_forever()

threading.Thread(target=run_event_loop, daemon=True).start()
loop_ready.wait()

# ---------- BLE Async Functions ----------
async def ble_connect():
    if ble_state["client"] and ble_state["client"].is_connected:
        return  # already connected

    print("Scanning for BLE device...")
    device = await BleakScanner.find_device_by_address(ble_state["device_address"])
    if not device:
        raise Exception("BLE device not found")

    client = BleakClient(device)
    await client.connect()
    await client.start_notify(NOTIFY_UUID, handle_notification)
    ble_state["client"] = client
    print("BLE connected.")

async def ble_disconnect():
    client = ble_state["client"]
    if client and client.is_connected:
        await client.stop_notify(NOTIFY_UUID)
        await client.disconnect()
        ble_state["client"] = None
        print("BLE disconnected.")

async def ble_send_cmd(cmd_bytes):
    if ble_state["client"] and ble_state["client"].is_connected:
        await ble_state["client"].write_gatt_char(WRITE_UUID, cmd_bytes)
    else:
        raise RuntimeError("Not connected to BLE device.")
    
async def ble_send_cmd_old(cmd_bytes: bytes):
    client = ble_state["client"]
    if not client or not client.is_connected:
        raise Exception("Not connected to BLE device")
    print(f"[SEND] {cmd_bytes.hex().upper()}")
    await client.write_gatt_char(WRITE_UUID, cmd_bytes)

# ---------- Flask Endpoints ----------


@app.route("/hello", methods=["GET"])
def hello():
    return "hello"
    
@app.route("/connect", methods=["GET"])
def connect():
    fut = asyncio.run_coroutine_threadsafe(ble_connect(), ble_state["loop"])
    try:
        fut.result(timeout=10)
        return jsonify({"status": "connected"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/disconnect", methods=["GET"])
def disconnect():
    fut = asyncio.run_coroutine_threadsafe(ble_disconnect(), ble_state["loop"])
    try:
        fut.result(timeout=10)
        return jsonify({"status": "disconnected"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/query/fileinfo", methods=["GET"])
def query_fileinfo_endpoint():
    global file_info_future
    
    if file_info_future is None:
        return jsonify({"error": "No file info available"}), 404

    try:
        # Check if future is done
        if file_info_future.done():
            file_info = file_info_future.result()
            return jsonify(file_info)
        else:
            # Future not done yet, wait up to 5 seconds
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            file_info = loop.run_until_complete(asyncio.wait_for(file_info_future, timeout=5))
            return jsonify(file_info)
    except asyncio.TimeoutError:
        return jsonify({"error": "Timeout waiting for file info"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/send", methods=["POST"])
def send_cmd():
    try:
        cmd = request.json.get("cmd")  # e.g., "play", "pause", "query_volume"
        if cmd == "play":
            cmd_bytes = play()
        elif cmd == "pause":
            cmd_bytes = pause()
        elif cmd == "volume":
            cmd_bytes = query_volume()
        else:
            return jsonify({"error": f"Unknown command '{cmd}'"}), 400

        fut = asyncio.run_coroutine_threadsafe(ble_send_cmd(cmd_bytes), ble_state["loop"])
        fut.result(timeout=5)
        return jsonify({"status": "sent", "cmd": cmd})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/file/playpause", methods=["POST"])
def file_play_pause():
    try:
        data = request.json
        serial = int(data.get("serial"))
        action = int(data.get("action"))

        cmd_bytes = play_or_pause_file(serial, action)
        asyncio.run_coroutine_threadsafe(ble_send_cmd(cmd_bytes), ble_state["loop"])

        return jsonify({
            "status": "sent",
            "command": "play_or_pause_file",
            "serial": serial,
            "action": "play" if action == 1 else "pause"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @app.route("/file/playpause", methods=["POST"])
# def file_play_pause():
#     try:
#         data = request.json
#         serial = int(data.get("serial"))
#         action = int(data.get("action"))  # 1 = play, 0 = pause

#         cmd_bytes = play_or_pause_file(serial, action)
#         fut = asyncio.run_coroutine_threadsafe(ble_send_cmd(cmd_bytes), ble_state["loop"])
#         fut.result(timeout=5)

#         return jsonify({
#             "status": "sent",
#             "command": "play_or_pause_file",
#             "serial": serial,
#             "action": "play" if action == 1 else "pause"
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0",  port=3000, debug = True, use_reloader=True)

# import asyncio
# import comm_test as comm 
# from flask import Flask
# import logging
# import functools
# print = functools.partial(print, flush=True)
# import sys
# sys.path.append('/usr/local/lib/python3.11/dist-packages/')

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
# 	return 'Hello World'

# @app.route('/play/<int:fileIndex>')
# async def play_file(fileIndex):
# 	#print('playing file at {0}'.format(fileIndex))
# 	# return
# 	print('enter getJSONReuslt', flush=True)
# 	#app.logger.info('This is an informational message')
# 	await comm.connected_device
# 	if not comm.connected_device:
# 		print("Play File: Device not found.")
# 		await comm.get_connected_device()
# 		#return 'Play File: device not found'
# 	comm.play_or_pause_file(fileIndex, 1)
# 	return 'playing file at ' + str(fileIndex)

# if __name__ == '__main__':
# 	#app.run()
# 	app.run(host='0.0.0.0', port=3000, debug = True)
# 	if not comm.connected_device:
# 		asyncio.run(comm.run())
# 		#return 'need to connect'
