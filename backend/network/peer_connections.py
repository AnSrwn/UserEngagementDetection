from common.log import Logger
from common.singleton import Singleton


@Singleton
class PeerConnections:
    connections = None

    def __init__(self):
        self.connections = {}

    def add(self, pc_id, connection):
        self.connections[pc_id] = connection

    def get(self, pc_id):
        return self.connections[pc_id]

    def remove(self, pc_id):
        try:
            self.connections.pop(pc_id)
        except Exception as e:
            Logger.instance().info(f"peer_connections remove {pc_id}: {e}")

    def length(self) -> int:
        return len(self.connections.items())
