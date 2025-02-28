import uuid

#物理演算・移動関連
GRAVITY = -0.002
JUMP_STRENGTH = 0.07
MOVE_SPEED = 0.05
MOUSE_SENSITIVITY = 0.15

#建造物(マルチでやるときは相手と同じ値にしないと)
ROOF_SIZE = 20
WALL_HEIGHT = 6
ENTRANCE_WIDTH = 5
ENTRANCE_HEIGHT = 4

#ネットワーク
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999
UPDATE_INTERVAL = 0.1
CLIENT_ID = str(uuid.uuid4())

#銃関連
FIRE_RATE = 0.1
RELOAD_DURATION = 3.0 #リロード機能内から意味ない.いつか追加

#プレイヤー
PLAYER_MAX_HP = 100
