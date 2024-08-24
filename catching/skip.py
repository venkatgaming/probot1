import socket

def is_connected():
    try:
        # Attempt to connect to a well-known server (Google's DNS server)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        # If the connection attempt fails, return False immediately
        return False

# Example usage
if not is_connected():
    print("No internet connection")
else:
    print("Internet is connected")
