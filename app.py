import socket
import threading
import random
import string
import os
import sys

# Define ANSI escape codes for colors
GREEN = '\033[92m'
CYAN = '\033[96m'
RED = '\033[91m'
RESET = '\033[0m'

# Global username variable
username = "Guest"

def clear_console():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_server_code():
    """Generate a random server code prefixed with 'celsium-'."""
    random_code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    return f"celsium-{random_code}"

def get_local_ip():
    """Get the local IP address of the host machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))  # Connect to a dummy external address
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Fallback to localhost if no connection
    finally:
        s.close()
    return ip

def start_server():
    global username
    host = get_local_ip()
    port = 0
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    assigned_port = server.getsockname()[1]
    server_code = generate_server_code()

    print(f"{GREEN}Server started! Share this code with friends to join:")
    print(f"Server Code: {server_code}")
    print(f"Server IP Address: {host}")
    print(f"Server is running on port {assigned_port} (Use this port to connect){RESET}")

    clients = []
    usernames = {}

    def handle_client(client_socket):
        """Handles each client's message and broadcasts it."""
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message.startswith("USERNAME:"):
                    usernames[client_socket] = message.split(":")[1]
                    broadcast(f"{usernames[client_socket]} has joined the chat!", None)
                else:
                    broadcast(f"{usernames[client_socket]}: {message}", client_socket)
            except:
                if client_socket in clients:
                    broadcast(f"{usernames[client_socket]} has left the chat.", None)
                    clients.remove(client_socket)
                client_socket.close()
                break

    def broadcast(message, sender_socket):
        """Broadcasts a message to all clients."""
        for client in clients:
            if client != sender_socket:
                client.send(message.encode('utf-8'))

    def send_message_from_host():
        """Allows the host to send messages to all clients."""
        while True:
            message = input(f"{CYAN}YourMessage (Host): {RESET}")
            broadcast(f"{username} (Host): {message}", None)

    # Start a thread to let the host send messages
    host_message_thread = threading.Thread(target=send_message_from_host, daemon=True)
    host_message_thread.start()

    while True:
        client_socket, address = server.accept()
        clients.append(client_socket)
        print(f"New connection from {address}")
        usernames[client_socket] = "Anonymous"
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

def join_server():
    global username
    code = input("Enter the server code (format: celsium-XXXXXXX): ")
    host = input("Enter the server's IP address: ")
    port = int(input("Enter the server's port: "))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(f"{GREEN}Connected to the server! Type your messages below:{RESET}")

    # Send username to the server
    client.send(f"USERNAME:{username}".encode('utf-8'))

    def receive_messages():
        """Receives and prints messages from the server in real-time."""
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                print(f"\r{GREEN}{message}{RESET}\nYou: ", end="")
            except:
                print(f"{RED}Disconnected from the server!{RESET}")
                client.close()
                break

    # Start a thread for receiving messages
    thread = threading.Thread(target=receive_messages, daemon=True)
    thread.start()

    while True:
        message = input("")  # Read user input
        print(f"{CYAN}YourMessage: {message}{RESET}")
        client.send(message.encode('utf-8'))

def set_username():
    global username
    username = input("Enter your desired username: ")
    print(f"Username set to: {GREEN}{username}{RESET}")
    main()

def main():
    clear_console()
    print("Welcome to CMD Chat App!")
    print("1. Host a server")
    print("2. Join a server")
    print("3. Set your username")
    print("0. Exit")
    choice = input("Enter your choice: ")
    
    if choice == '1':
        start_server()
    elif choice == '2':
        join_server()
    elif choice == '3':
        set_username()
    elif choice == '0':
        print("Exiting... Goodbye!")
        sys.exit()
    else:
        print(f"{RED}Invalid choice! Try again.{RESET}")
        main()

if __name__ == "__main__":
    main()
