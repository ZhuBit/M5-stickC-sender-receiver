import socket
import csv
import time
from threading import Thread, Lock
import os

os.makedirs('data', exist_ok=True)

# Server settings
HOST = '10.42.0.1'  # server IP
PORT = 5005      # server port

# Create a socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)  # listen for up to 2 connections

CSV_COLUMN_NAMES = ['sync_flag', 'IMU_stopwatch', 'GX', 'GY', 'GZ', 'AX', 'AY', 'AZ',
                    'receive_timestamp', 'buffer_save_timestamp']

print("Server started, waiting for connections...")

# Collect user ID
user_id = input("Enter a user ID: ")
print("Waiting for watches to connect...")
# Initialize connections
conn1, addr1 = server.accept()
conn2, addr2 = server.accept()

# Receive hand identifiers from watches
hand1 = conn1.recv(1024).decode().strip()
hand2 = conn2.recv(1024).decode().strip()
print(hand1, hand2)

# Create csv writers for both watches
file1 = open(f"./data/{user_id}_{hand1}.csv", "w", newline='')
file2 = open(f"./data/{user_id}_{hand2}.csv", "w", newline='')

writer1 = csv.writer(file1)
writer2 = csv.writer(file2)

# Write column names to CSV files
writer1.writerow(CSV_COLUMN_NAMES)
writer2.writerow(CSV_COLUMN_NAMES)

print(f"Connected to watch1 ({hand1}) at {addr1} and watch2 ({hand2}) at {addr2}")

# Await user command to start
input("Press ENTER to start the test")

start_command = f"S".encode()
conn1.sendall(start_command)
conn2.sendall(start_command)

# Global buffers for data and locks
data_buffer_watch1 = []
data_buffer_watch2 = []
buffer_lock1 = Lock()
buffer_lock2 = Lock()

def handle_watch(conn, buffer, buffer_lock):
    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                print("No data received!!!")
            elif data == "End":
                print("End signal received, closing connection.")
                break
            else:
                with buffer_lock:
                    print('Data received:', data)
                    new_server_time = str(int(time.time() * 1000))
                    data = data + ',' + new_server_time
                    buffer.append(data)
        except ConnectionResetError:
            print("Connection was reset. Ending data collection for this watch.")
        except Exception as e:
            print(f"An error occurred: {e}")

def write_buffer_to_csv(buffer, writer, buffer_lock):
    while True:
        with buffer_lock:
            if buffer:
                for data in buffer:
                    cleaned_data = data.replace('"', '').strip()

                    # Append new buffer time to each data point
                    new_buffer_time = str(int(time.time() * 1000))
                    cleaned_data_with_time = cleaned_data + ',' + new_buffer_time

                    writer.writerow(cleaned_data_with_time.split(','))
                buffer.clear()
        print("Buffer is SAVED, sleeping..........................................")
        time.sleep(1)  # Adjust the sleep time as needed (in sec )

# Start threads to handle both watches
thread1 = Thread(target=handle_watch, args=(conn1, data_buffer_watch1, buffer_lock1))
thread2 = Thread(target=handle_watch, args=(conn2, data_buffer_watch2, buffer_lock2))

# Start writer threads
writer_thread1 = Thread(target=write_buffer_to_csv, args=(data_buffer_watch1, writer1, buffer_lock1))
writer_thread2 = Thread(target=write_buffer_to_csv, args=(data_buffer_watch2, writer2, buffer_lock2))

thread1.start()
thread2.start()
writer_thread1.start()
writer_thread2.start()

input("Press ENTER to end the test")

# Send 'End' command to both watches
conn1.sendall(b"End\n")
conn2.sendall(b"End\n")

# Wait for threads to finish and close connections
thread1.join()
thread2.join()
writer_thread1.join()
writer_thread2.join()

# Close csv files
file1.close()
file2.close()

conn1.close()
conn2.close()

print("Test ended")
