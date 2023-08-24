from common.singleton import Singleton


@Singleton
class PeerConnections:
    connections = None

    def __init__(self):
        self.connections = set()

    def add(self, connection):
        self.connections.add(connection)

    def discard(self, connection):
        self.connections.discard(connection)

    def length(self) -> int:
        return len(self.connections)
