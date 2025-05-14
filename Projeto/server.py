import threading
import socket
import time
from time import sleep

# Server IP and port configuration
SERVER_IP = '2001:0690:2280:0828::3'
SERVER_PORT_1 = 5001
SERVER_PORT_2 = 5002

# Create socket to listen to RSU 1
sock_1 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sock_1.bind((SERVER_IP, SERVER_PORT_1))

# Create socket to listen to RSU 2
sock_2 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sock_2.bind((SERVER_IP, SERVER_PORT_2))

server_tag = 0


# Returns the average speed of the vehicles
def average(speed):
    return sum(speed) / len(speed)


# Format of message to send [server_tag:NºVehicles:Recomended_Velocity]
def define_format(number_of_vehicles, average_speed):
    return f"{server_tag}:{len(number_of_vehicles)}:{int(average(average_speed))}:{time.time()}", int(average(average_speed))


# Analyze the data to store the information in the lists
def analyze_data(data_received, number_of_vehicles, average_speed):
    data_list = data_received.split(":")

    if int(data_list[1]) not in number_of_vehicles:
        number_of_vehicles.append(int(data_list[1]))  # Append the vehicle ID in variable

    average_speed.append(int(data_list[3]))  # Append the vehicle velocity in variable

    return number_of_vehicles, average_speed


def receive_messages_1():
    packets_received = list()  # Create a variable to store the packets received

    number_of_vehicles_1 = list()  # Create a variable to store the number o vehicles in RSU 1
    average_speed_1 = list()  # Create a variable to store the velocity of vehicles in RSU 1

    danger_string = f"{server_tag}:DANGER:Slow Down"

    sock_1.listen()  # Listen in the socket for a connection
    client_1, addr_1 = sock_1.accept()  # Accepts the connection
    print(f"{addr_1}_Accepted!!!!")

    while True:
        # Receive data from the server
        data_ = client_1.recv(1024)  # Receives the data from the RSU
        received_data = data_.decode()  # Decode the data received
        packets_received.append(received_data)  # Stores the data in a list

        print("Received message:", received_data)

        number_of_vehicles_1, average_speed_1 = analyze_data(received_data, number_of_vehicles_1,
                                                             average_speed_1)  # Calculates the informartion

        data_to_send, speed = define_format(number_of_vehicles_1,
                                            average_speed_1)  # Defines the format of the messages to be sent

        if speed < 90:     # If speed is higher than 100 Km/h send DANGER message
            print(f"Informação enviada: {data_to_send}")
            client_1.send(data_to_send.encode())

        else:   # If not, send informational message to the RSU
            print(f"Informação enviada: {data_to_send}")
            client_1.send((danger_string + f":{time.time()}").encode())

        sleep(0.5)


def receive_messages_2():
    packets_received = list()  # Create a variable to store the packets received

    number_of_vehicles_2 = list()  # Create a variable to store the number o vehicles in RSU 2
    average_speed_2 = list()  # Create a variable to store the velocity of vehicles in RSU 1

    danger_string = "DANGER:Slow_Down"

    sock_2.listen()  # Listen in the socket for a connection
    client_2, addr_2 = sock_2.accept()  # Accepts the connection
    print(f"{addr_2}_Accepted!!!!")

    while True:
        # Receive data from the server
        data_ = client_2.recv(1024)  # Receives the data from the RSU
        received_data = data_.decode()  # Decode the data received
        packets_received.append(received_data)  # Stores the data in a list

        number_of_vehicles_2, average_speed_2 = analyze_data(received_data, number_of_vehicles_2,
                                                             average_speed_2)  # Calculates the informartion

        data_to_send, speed = define_format(number_of_vehicles_2,
                                            average_speed_2)  # Defines the format of the messages to be sent

        if speed < 100:
            print(data_to_send)
            client_2.send(data_to_send.encode())
        else:
            print(danger_string)
            client_2.send(danger_string.encode())

        sleep(0.5)


if __name__ == "__main__":
    # Configure a thread to receive the incoming messages from RSU 1
    receive_thread_1 = threading.Thread(target=receive_messages_1)
    # Configure a thread to receive the incoming messages from RSU 2
    receive_thread_2 = threading.Thread(target=receive_messages_2)

    receive_thread_1.start()
    receive_thread_2.start()

    receive_thread_1.join()
    receive_thread_2.join()

    # Close the sockets
    sock_1.close()
    sock_2.close()
