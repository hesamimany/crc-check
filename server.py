import socket
import threading
import random
import zlib

clients = []
threads=[]

def calculate_crc(data):
    return zlib.crc32(data) & 0xffffffff

def corrupt_data(data):
    if random.random() < 0.30:  # 5% chance to corrupt the data
        index = random.randint(0, len(data) - 1)
        corrupted_bit = '0' if data[index] == '1' else '1'
        print(f"corrupting data!\nbefore: {data}\nafter: {data[:index] + corrupted_bit + data[index+1:]}")
        return data[:index] + corrupted_bit + data[index+1:]
        
    return data

def handle_client(client_socket, clients, address):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break

            # Extract data and CRC
            data = message[:-32]
            received_crc = message[-32:]
            
            # Validate CRC
            # calculated_crc = calculate_crc(data)
            # if calculated_crc != received_crc:
            #     print("Error detected: CRC mismatch")
            #     continue

            # Possibly corrupt the data
            data = corrupt_data(data.decode())
            data = data.encode()

            # Recalculate CRC after potential corruption
            # new_crc = calculate_crc(data).to_bytes(4, byteorder='big')

            # Broadcast the message to other clients
            for client in clients:
                if client != client_socket:
                    client.send(data+received_crc)
        except Exception as e:
            print(f"Client disconnected: {e}")
            break

    client_socket.close()
    clients.remove(client_socket)

def server_program():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(5)
    print("Server listening on port 12345")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)
        threads.append(threading.Thread(target=handle_client, args=(client_socket, clients, addr)))

        if len(clients) >= 2:
            for t in threads:
                if not t.is_alive():
                    t.start()

if __name__ == "__main__":
    server_program()
