import socket
import json
import time
import threading
from config import SERVER_IP, SERVER_PORT, UPDATE_INTERVAL, CLIENT_ID

class NetworkManager:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.server_addr = (SERVER_IP, SERVER_PORT)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.remote_players = {} 
        self.remote_bullets = [] 
        self.player_hp = 100
        self.lock = threading.Lock()
        self.running = True

    def start_receiving(self):
        thread = threading.Thread(target=self._network_receive, daemon=True)
        thread.start()

    def _network_receive(self):
        time.sleep(0.5)
        while self.running:

            try:
                stale = [pid for pid, pdata in self.remote_players.items() 
                if current_epoch - pdata["last_comm"] > 1.0]
                for stale_pid in stale:
                    del self.remote_players[stale_pid]
            except:
                pass

            try:
                data, addr = self.udp_sock.recvfrom(4096)
                msg = json.loads(data.decode())
                msg_type = msg.get("type", "state")
                current_epoch = time.time() 
                if msg_type == "state":
                    pid = msg.get("id")
                    if pid == self.client_id:
                        continue
                    new_pos = msg.get("pos")
                    new_yaw = msg.get("yaw")
                    new_pitch = msg.get("pitch")
                    with self.lock:
                        if pid not in self.remote_players:
                            self.remote_players[pid] = {
                                "pos": new_pos,
                                "yaw": new_yaw,
                                "pitch": new_pitch,
                                "target_pos": new_pos,
                                "last_comm": current_epoch
                            }
                        else:
                            self.remote_players[pid]["target_pos"] = new_pos
                            self.remote_players[pid]["yaw"] = new_yaw
                            self.remote_players[pid]["pitch"] = new_pitch
                            self.remote_players[pid]["last_comm"] = current_epoch

                elif msg_type == "bullet":
                    if msg.get("id") != self.client_id:
                        with self.lock:
                            self.remote_bullets.append({
                                "pos": msg.get("pos"),
                                "dir": msg.get("dir"),
                                "speed": 0.5,
                                "spawn_time": current_epoch,
                                "lifetime": 3.0
                            })
                elif msg_type == "damage":
                    damage = msg.get("amount", 0)
                    with self.lock:
                        self.player_hp -= damage
            except Exception as e:
                print(e)

    def send(self, msg):
        try:
            self.udp_sock.sendto(json.dumps(msg).encode(), self.server_addr)
        except Exception as e:
            print(e)

    def stop(self):
        self.running = False
        self.udp_sock.close()
