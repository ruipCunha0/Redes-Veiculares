import socket
import struct
import threading
from time import sleep

# Multicast group & port configuration
MULTICAST_GROUP = 'FF02::1'
MULTICAST_PORT = 5000

# Socket construction for IPV6
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind the socket to the IPv6 address
sock.bind(('::', MULTICAST_PORT))

request = struct.pack("16sI", socket.inet_pton(socket.AF_INET6, MULTICAST_GROUP), 0)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, request)


def receive_messages_from_server():
    while True:
        data = server.recv(1024)  # Receive the data from the server
        print(f"Recebido do servidor: {data.decode()}\n")

        sock.sendto(data, (MULTICAST_GROUP, MULTICAST_PORT, 0, 0))  # Sends the data received from the Server to the multicast socket

        sleep(0.5)  # Delay the send_thread for about ~ 0.5 sec


def receive_messages(rsu_id):
    # Store the information related to the vehicles in a dictionary
    # {"IPV6_ADDRESS" -> "CAR_INFORMATION"}
    packets_received = list()

    while True:
        packet = sock.recvfrom(1024)  # Receive the data from the vehicles
        data, address = packet
        data_list = data.decode().split(":")

        if data.decode() not in packets_received:
            if int(data_list[0]) == 0:
                pass
            else:
                packets_received.append(data.decode())  # Stores the data received in list

                sock.sendto(data, (MULTICAST_GROUP, MULTICAST_PORT, 0, 0))  # Sends the data received from the vehicles to the multicast socket
                print(f"Recebido: {data.decode()}\n")

                if int(data_list[0]) != 0:
                    data = f"{rsu_id}:{data.decode()}"  # Add the RSU ID to the data
                    server.send(data.encode())  # Sends the data with the RSU ID to the server

        sleep(0.5)  # Delay the send_thread for about ~ 0.5 sec


if __name__ == "__main__":

    rsu_Id = int(input("Digite o ID da RSU: "))

    if rsu_Id == 1:
        # Server IP and port configuration
        SERVER_IP = '2001:0690:2280:0828::3'
        SERVER_PORT = 5001

        # Socket construction for IPV6 Server
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.connect((SERVER_IP, SERVER_PORT))

    else:
        # Server IP and port configuration
        SERVER_IP = '2001:0690:2280:0828::3'
        SERVER_PORT = 5002

        # Socket construction for IPV6 Server
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.connect((SERVER_IP, SERVER_PORT))

    # Configure a thread to receive the incoming messages
    receive_thread = threading.Thread(target=receive_messages, args=(rsu_Id, ))
    # Configure a thread to send messages
    send_thread = threading.Thread(target=receive_messages_from_server)

    receive_thread.start()
    send_thread.start()

    send_thread.join()
    receive_thread.join()

    # Close the sockets
    sock.close()
    server.close()
