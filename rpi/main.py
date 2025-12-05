import socket
import time
import json
from lights import lights
from stepper import stepper
import gdmath
from readangle import read_angle_f
import threading

UDP_HOST = "steamdeck"
UDP_PORT_LOCAL = 4444
UDP_PORT_NETWORKED = 4433

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", UDP_PORT_LOCAL))
sock.setblocking(0)

def send_json(data):
    message = json.dumps(data).encode('utf-8')
    sock.sendto(message, (UDP_HOST, UDP_PORT_NETWORKED))

def receive_json():
    try:
        data, _ = sock.recvfrom(1024)
        return json.loads(data.decode('utf-8'))
    except BlockingIOError:
        return None

local_rotation: float = 0
local_delta: float = 0
remote_rotation: float = 0
remote_delta: float = 0

def motor_rotation_fn():
    global remote_rotation
    while True:
        target_pos = stepper.fpos_to_pos(remote_rotation)
        stepper.single_step_towards(target_pos) # blocking / time.sleep

def read_thread_fn():
    global local_rotation, local_delta
    while True:
        old_rotation = local_rotation
        local_rotation = read_angle_f()
        local_delta = gdmath.shortest_diff(old_rotation, local_rotation)
        lights.expected_rotation_delta_local = local_delta
        lights.rotation_local = local_rotation
        try:
            send_json({"value": local_rotation, "delta": local_delta})
        except Exception as e:
            print("Error sending data:", e)
        time.sleep(0.01)

def lights_fn():
    global local_rotation, local_delta, remote_rotation, remote_delta
    last_time = time.time()
    delta = 1/60
    while True:
        lights.color = gdmath.sample_color_gradient((local_rotation + remote_rotation) / 2)
        lights.process(delta)
        time.sleep(1/60)
        current_time = time.time()
        delta = current_time - last_time
        last_time = current_time

def network_recv_fn():
    global remote_rotation, remote_delta
    while True:
        data = receive_json()
        if data:
            if "value" in data:
                remote_rotation = data["value"]
                lights.rotation_remote = remote_rotation
            if "delta" in data:
                remote_delta = data["delta"]
                lights.expected_rotation_delta_remote = remote_delta
        time.sleep(0.01)

motor_thread = threading.Thread(target=motor_rotation_fn)
motor_thread.start()
read_thread = threading.Thread(target=read_thread_fn)
read_thread.start()
lights_thread = threading.Thread(target=lights_fn)
lights_thread.start()
network_thread = threading.Thread(target=network_recv_fn)
network_thread.start()

motor_thread.join()
read_thread.join()
lights_thread.join()
network_thread.join()