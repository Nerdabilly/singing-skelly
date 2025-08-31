import comm_test as comm
import asyncio
import sys
import threading


hexstr = "BBC6000D0101250000000078"
serial = int(hexstr[4:8], 16)
playing = int(hexstr[8:10], 16)
duration = int(hexstr[10:14], 16)

a = int(hexstr[14:14], 16)
b = int(hexstr[10:14], 16)
c = int(hexstr[10:14], 16)



