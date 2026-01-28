from space_network_lib import *
import time

class BrokenConnectionError(CommsError):
    pass

class Satellite(SpaceEntity):
    def receive_signal(self, packet: Packet):
        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            inner_packet.sender = self
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            transmission_attempt(inner_packet)
        else:
            print(f"Final destination reached: {packet.data}")

class Earth(SpaceEntity):
    def receive_signal(self, packet: Packet):
        pass

class RelayPacket(Packet):
    def __init__(self, packet_to_relay,sender, proxy):
        super().__init__(data=packet_to_relay, sender=sender, receiver=proxy)


    def __repr__(self):
        return f"RelayPacket(Relaying[{self.data}]to{self.receiver}from{self.sender})"

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

earth=Earth("Earth",0)
sat1 = Satellite("Sat1", 100)
sat2 = Satellite("Sat2", 200)

#my_packet = Packet("You're going to hit a rock!", sat1, sat2)

final_p = Packet("Hello from Earth!!", sat1, sat2)

earth_to_sat1_p = RelayPacket(final_p, earth, sat1)

try:
    transmission_attempt(earth_to_sat1_p)
except BrokenConnectionError:
    print("Transmission failed")
