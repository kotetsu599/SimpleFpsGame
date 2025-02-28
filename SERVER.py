import socket
import json
import threading

SERVER_IP = "0.0.0.0"
SERVER_PORT = 9999

clients = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))
print("サーバー起動:", SERVER_IP, SERVER_PORT)

def handle_message(data, addr):
    try:
        msg = json.loads(data.decode())
    except Exception as e:
        print("Decode error:", e)
        return

    client_id = msg.get("id")
    if client_id:
        clients[client_id] = addr

    msg_type = msg.get("type", "state")
    if msg_type in ["state", "bullet"]:
        for cid, client_addr in list(clients.items()):
            try:
                sock.sendto(json.dumps(msg).encode(), client_addr)
            except Exception as e:
                print(e)

                del clients[cid]
    elif msg_type == "hit":
        target = msg.get("target")
        damage = msg.get("damage", 10)
        shooter = msg.get("shooter")
        if target in clients:
            damage_msg = {
                "type": "damage",
                "amount": damage,
                "shooter": shooter
            }
            try:
                sock.sendto(json.dumps(damage_msg).encode(), clients[target])
            except Exception as e:
                print(e)
                del clients[target]

        for cid, client_addr in list(clients.items()):
            try:
                sock.sendto(json.dumps(msg).encode(), client_addr)
            except Exception as e:
                print(e)
                del clients[cid]

def server_loop():
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=handle_message, args=(data, addr), daemon=True).start()
        except socket.error as e:
            if e.errno == 10054:
                print(e)
            else:
                print(e)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    server_loop()
