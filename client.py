import socket
import threading
import zlib
import traceback


def xor(a, b):
    # Perform XOR between two binary strings
    result = []
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')
    return ''.join(result)

def mod2div(dividend, divisor):
    # Perform modulo-2 division
    pick = len(divisor)
    tmp = dividend[0:pick]
    
    while pick < len(dividend):
        if tmp[0] == '1':
            tmp = xor(divisor, tmp) + dividend[pick]
        else:
            tmp = xor('0'*pick, tmp) + dividend[pick]
        pick += 1
    
    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0'*pick, tmp)
    
    checkword = tmp
    return checkword

def calculate_crc(data):
    crc = format(zlib.crc32(data), 'b')
    if(len(crc)<32):
        for i in range(32-len(crc)):
            crc+="0"+crc
    return crc

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(2048)
            if not message:
                break
            
            # Extract data and CRC
            data = message[:-32]
            received_crc = message[-32:].decode()
            
            # Validate CRC
            calculated_crc = calculate_crc(data)
            
            print(f"message: {message} and message size = {len(message)}")
            print(f"data: {data} and data size = {len(data)}")
            print(f"calculated crc: {calculated_crc} and calculated crc size = {len(calculated_crc)}")
            
            if calculated_crc != received_crc:
                print(f"Error detected: CRC mismatch\nCalculated crc: {calculated_crc}\nReceived crc:   {received_crc}")
                fixable=False
                corrected_data = []
                # Find the error bit position by checking each bit
                for i in range(len(data)):
                    # Flip the bit at position i
                    corrected_data = [*data.decode()]
                    corrected_data[i] = '1' if corrected_data[i] == '0' else '0'
                    corrected_data = ''.join(corrected_data)
                    
                    # Recalculate CRC
                    new_crc = calculate_crc(corrected_data.encode())
                    
                    # If the new CRC matches the received CRC, correction is successful
                    if new_crc == received_crc:
                        print(f"Error detected and corrected at bit position {i}.")
                        fixable=True
                        break
                if not fixable:
                    print("Error correction failed.")
                    continue
                else:
                    print(f"Corrected data is: {corrected_data}")
                    continue
            else:
                print(f"\n\n# # # # # # # # # # \nReceived: {data.decode()} from {client_socket.getsockname()}\n# # # # # # # # # #\n\n")
        except Exception as e:
            print(f"Error receiving message: {e}")
            print(traceback.format_exc())
            break

def send_messages(client_socket):
    while True:
        message = input("Enter binary data: ")
        if not all(c in '01' for c in message):
            print("Invalid input. Please enter binary data.")
            continue

        data = message.encode()
        crc = calculate_crc(data)
        client_socket.send(data + crc.encode())

def client_program():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    threading.Thread(target=send_messages, args=(client_socket,)).start()

if __name__ == "__main__":
    client_program()
