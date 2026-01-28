from space_network_lib import *
import time

class BrokenConnectionError(CommsError):
    pass

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

        except LinkTerminatedError:
            print("link lost")
            raise BrokenConnectionError("Connection permanently lost")

        except OutOfRangeError:
            print("Target out of range")
            raise BrokenConnectionError("Target is too far away")


network = SpaceNetwork(level=3)


sat1 = Satellite("Sat1", 100)
sat2 = Satellite("Sat2", 200)

my_packet = Packet("You're going to hit a rock!", sat1, sat2)

try:
    transmission_attempt(my_packet)
except BrokenConnectionError:
    print("Transmission failed")
