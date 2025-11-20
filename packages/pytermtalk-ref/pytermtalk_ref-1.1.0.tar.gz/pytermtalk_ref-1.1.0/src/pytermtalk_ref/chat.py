# src/pytermtalk_ref/chat.py
# original script taken from Linux Magazine - Octobre 2025 by Andrea Ciarrocchi
"""
A Python reference implementation of a terminal-based chat program using sockets.
Supports both server and client modes. This project serves as a starting point
for building a production-ready terminal chat application.

Warning: This script does **not** provide authentication. 
         Do **not** use it for production or sensitive purposes.

Original script by Andrea Ciarrocchi was published in Linux Magazine, October 2025.
"""

import socket
import threading


# Configuration

HOST, PORT = "127.0.0.1", 5555
clients = []


# -----------------------------------------------------------------------------
#   server code / Funcion: handle_client()
# -----------------------------------------------------------------------------


def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{client_address}: {message}")
            broadcast(message, client_socket)
        except:
            break
    print(f"[DISCONNECT] {client_address} disconnected.")
    client_socket.close()


# -----------------------------------------------------------------------------
#   server code / Funcion: broadcast()
# -----------------------------------------------------------------------------


def broadcast(message, sender_socket=None):
    """Send message to all connected clients (by the server)."""
    for client in clients:
        if client != sender_socket:
            # don't send the message to the sender self
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                clients.remove(client)


# -----------------------------------------------------------------------------
#   server code / Funcion: send_server_messages()
# -----------------------------------------------------------------------------


def send_server_messages():
    while True:
        message = input()
        broadcast(f"[SERVER]: {message}")


# -----------------------------------------------------------------------------
#   server code / Funcion: start_server()
# -----------------------------------------------------------------------------


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    threading.Thread(target=send_server_messages, daemon=True).start()

    while True:
        cl_socket, cl_address = server.accept()
        clients.append(cl_socket)
        thread = threading.Thread(target=handle_client, args=(cl_socket, cl_address))
        thread.start()


# -----------------------------------------------------------------------------
#   client code / Funcion: receice_messages()
# -----------------------------------------------------------------------------


def receive_messages(client_socket):
    """Receive forever messages from server,  non-blocking threaded function."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except:
            print("[ERROR] Connection lost.")
            break


# -----------------------------------------------------------------------------
#   client code / Funcion: start_client()
# -----------------------------------------------------------------------------


def start_client():
    """Start the client and send forever messages to the server."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST,PORT))
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # forever: input text and send msg to server
    while True:
        message = input()
        client.send(message.encode('utf-8'))

    # RikR - print("start_client(): about executing 'client.close()'")
    # RikR - todo: the close() should be in a final-block probably 
    client.close()  # RikR todo: this line is never executed


# -----------------------------------------------------------------------------
#   Funcion main()
# -----------------------------------------------------------------------------


def main():
    """Entry point program: start as server or as client."""

    print("\nWarning: do not use in production environments or for exchanging " +
          "sensitive information!\n")
    choice = input("Start server or client? (s/c): ").strip().lower()
    if choice == 's':
        start_server()
    elif choice == 'c':
        start_client()


# -----------------------------------------------------------------------------
#   module startup from terminal: 
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# === END ===
