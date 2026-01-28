from space_network_lib import *
import time

class Satellite(SpaceEntity):
    def receive_signal(self, packet: Packet):
        print(f"[{self.name}] Received: {packet}")

def transmission_attempt(packet):
    while True:
        try:
            network.send(packet)
            break

        except TemporalInterferenceError:
            print("Interference, waiting...")
            time.sleep(2)

        except DataCorruptedError:
            print("Data corrupted, retrying...")


network = SpaceNetwork(level=2)


sat1 = Satellite("Sat1", 100)
sat2 = Satellite("Sat2", 200)

my_packet = Packet("You're going to hit a rock!", sat1, sat2)

transmission_attempt(my_packet)