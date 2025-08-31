import asyncio
from bleak import BleakScanner

async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        name = d.name or "Unknown"
        address = d.address
        print(f"Name: {name}, Address: {address}")

asyncio.run(scan())
