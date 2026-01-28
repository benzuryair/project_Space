from space_network_lib import *

class Satellite(SpaceEntity):
    def receive_signal(self, packet: Packet):
        print(f"[{self.name}] Received: {packet}")

network = SpaceNetwork(level=1)

sat1 = Satellite("Sat1", 100)
sat2 = Satellite("Sat2", 200)

my_packet = Packet("You're going to hit a rock!", sat1, sat2)

network.send(my_packet)