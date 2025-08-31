import argparse
import json
import socket
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765

def send_command(cmd_dict):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_HOST, SERVER_PORT))
        client.sendall(json.dumps(cmd_dict).encode())
        response = client.recv(4096)
        print(response.decode())
        client.close()
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="BLE CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    playpause = subparsers.add_parser("playpause", help="Play/pause a file")
    playpause.add_argument("--serial", type=int, required=True, help="Serial number")
    playpause.add_argument("--action", type=int, choices=[0, 1], required=True, help="0=pause, 1=play")

    query = subparsers.add_parser("query_file_info", help="Query file info")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    send_command(vars(args))

if __name__ == "__main__":
    main()
