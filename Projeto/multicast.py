import random
import socket
import struct
import threading
import time
from time import sleep
from colorama import Fore, Back, Style

import vehicle as v

# Multicast group & port configuration
MULTICAST_GROUP = 'FF02::1'
MULTICAST_PORT = 5000

# Possible velocities for a vehicle
vehicle_velocities = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]

# Socket construction for IPV6
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# Allow multiple copies of this program on one machine
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IP_MULTICAST_TTL, True)

# Bind the socket to the IPv6 address
sock.bind(('::', MULTICAST_PORT))

request = struct.pack("16sI", socket.inet_pton(socket.AF_INET6, MULTICAST_GROUP), 0)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, request)


# Format of message to send [ID:Vehicle_Type:Velocity:Position:Timestamp]
def define_format(vehicle):
    position_x, position_y = vehicle_object.get_position()  # Get the current positions
    vehicle_object.set_position((position_x + random.randrange(100, 300)),
                                (position_y + random.randrange(100, 300)))  # Set the positions to a random number

    return f'{vehicle.get_ID()}:{vehicle.get_type()}:{vehicle.get_velocity()}:{vehicle.get_position()}:{time.time()}'


def calculate_delay(data_list):
    now = time.time()  # Get time now

    delay_seconds = now - float(data_list[-1])  # Calculate the delay
    delay_milliseconds = delay_seconds * 1000  # Calculate the delay in microsenconds

    return delay_milliseconds.__round__(2)


def receive_messages(vehicle_ID):
    packets_received = list()

    while True:
        packet = sock.recvfrom(1024)  # Receive the data from the Vehicles and RSU
        data, address = packet
        data_list = data.decode().split(":")  # Slip the data into a list

        # If the data is received from the server
        if int(data_list[0]) == vehicle_ID:
            pass
        elif data.decode() not in packets_received:

            if int(data_list[0]) == 0:
                if data_list[1] == 'DANGER':
                    print(Fore.RED + f"Recebido do Servidor: {data.decode()}     delay: {calculate_delay(data_list)} ms\n")
                else:
                    print(Fore.GREEN + f"Recebido do Servidor: {data.decode()}     delay: {calculate_delay(data_list)} ms\n")
            else:
                packets_received.append(data.decode())  # Store the data in a list
                print(f"Recebido: {data.decode()}     delay: {calculate_delay(data_list)} ms\n")
                sock.sendto(data,
                            (MULTICAST_GROUP, MULTICAST_PORT, 0, 0))  # Sends the data received to the multicast socket

        sleep(0.5)  # Delay the send_thread for about ~ 0.5 sec


def send_messages(vehicle):
    while True:
        vehicle_object.set_velocity(random.choice(vehicle_velocities))  # Set a random velocity

        message = define_format(vehicle)  # Defines the message to be sent

        print(Fore.WHITE + f"Mensagem enviada: {message}")  # Prints the message sent with timestamp

        sock.sendto(message.encode(), (MULTICAST_GROUP, MULTICAST_PORT, 0, 0))

        sleep(15)  # Delay the send_thread for about ~ 10 sec


if __name__ == "__main__":
    vehicle_Id = int(input("Digite o ID do veiculo: "))
    vehicle_Type = input("Digite o tipo de veiculo: ")
    vehicle_X = int(input("Digite as coordenadas X do veiculo: "))
    vehicle_Y = int(input("Digite as coordenadas Y do veiculo: "))

    vehicle_object = v.Vehicle(vehicle_Id, vehicle_Type, vehicle_X, vehicle_Y)  # Create a class vehicle

    # Configure a thread to receive the incoming messages
    receive_thread = threading.Thread(target=receive_messages, args=(vehicle_Id,))
    # Configure a thread to send messages
    send_thread = threading.Thread(target=send_messages, args=(vehicle_object,))

    receive_thread.start()
    send_thread.start()

    send_thread.join()
    receive_thread.join()

    sock.close()  # Close the socket
