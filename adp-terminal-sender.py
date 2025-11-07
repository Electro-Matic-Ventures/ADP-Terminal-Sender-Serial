import socket
import argparse
import re
from random import randint
import time
from datetime import datetime
import serial


def parse_message(message):
    parts = re.split(r'(\\[xX][0-9A-Fa-f]{2})', message)
    parts = [e for e in parts if e != '']
    parsed_message = b''
    for part in parts:
        if part.startswith('\\x') or part.startswith('\\X'):
            parsed_message += bytes.fromhex(part[2:])
        else:
            parsed_message += part.encode('utf-8')
    return parsed_message

def send_tcpip(ip, port, parsed_message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.sendall(parsed_message)
    s.close()
    print(f'{datetime.now()} -- sent -- {parsed_message}')

def send_serial(parsed_message):
        a="COM3"
        b=9600
        c=serial.EIGHTBITS
        d=serial.PARITY_NONE
        e=serial.STOPBITS_ONE
        f=1.0
        try:
            with serial.Serial(port=a,baudrate=b,bytesize=c,parity=d,stopbits=e,timeout=f) as s:
                s.write(parsed_message)
                s.flush()
                return f"message sent: {parsed_message}"
        except Exception as e:
            return f"Failed to send message: {e}"

def send_from_input(ip, port, message):
    parsed_message = parse_message(message)
    # send_tcpip(ip, port, parsed_message)
    send_serial(parsed_message)

def send_from_file(ip, port, filename, interval):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file]
    while True:
        line_number = randint(0,len(lines)-1)
        line = lines[line_number]
        parsed_message = parse_message(line)
        # send_tcpip(ip, port, parsed_message)
        send_serial(parsed_message)
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send a TCP message')
    parser.add_argument('--ip', type=str, help="Target IP address")
    parser.add_argument('--port', type=int, help="Target port number")
    parser.add_argument('-t', '--text', type=str, help="Message in format \\x01\\xF7")
    parser.add_argument('-f', '--file', type=str, help="File containing messages line by line")
    parser.add_argument('-i', '--interval', type=float, help="Interval between messages in seconds")
    args = parser.parse_args()

    if not args.ip:
        parser.error("Target IP address (--ip) must be provided")
    if not args.port:
        parser.error("Target port number (--port) must be provided")

    if args.text:
        send_from_input(args.ip, args.port, args.text)
    elif args.file:
        if not args.interval:
            parser.error("--interval must be provided when using --file")
        send_from_file(args.ip, args.port, args.file, args.interval)
    else:
        parser.error("Either -t/--text or -f/--file must be provided")
