from space_network_lib import *
import time


class BrokenConnectionError(CommsError):
    pass


class SecurityBreachError(CommsError):
    pass


class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth, key):
        super().__init__(name, distance_from_earth)
        self.key = key

    def receive_signal(self, packet: Packet):
        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            inner_packet.sender = self
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            transmission_attempt(inner_packet)
        else:
            if isinstance(packet, EncryptedPacket):
                if packet.receiver == self:
                    try:
                        decrypted = packet.decrypt_key(self.key)
                        print(f"[{self.name}] Decrypted message: {decrypted}")
                    except SecurityBreachError:
                        print(f"[{self.name}] Security breach detected!")
            else:
                print(f"[{self.name}] Final destination reached: {packet.data}")


class Earth(SpaceEntity):
    def receive_signal(self, packet: Packet):
        pass


class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(data=packet_to_relay, sender=sender, receiver=proxy)

    def __repr__(self):
        return f"RelayPacket(Relaying[{self.data}]to{self.receiver}from{self.sender})"


class EncryptedPacket(Packet):
    SIGNATURE = "MSG|"
    def __init__(self, data, sender, receiver,key):
        self._encryption_key = key
        signed_data = self.SIGNATURE + data
        encrypted_data = self.encrypted_fun(signed_data, key)
        super().__init__(encrypted_data, sender, receiver)


    def decrypt_key(self, key):
        decrypted = self.encrypted_fun(self.data, key)
        if not decrypted.startswith(self.SIGNATURE):
            raise SecurityBreachError("Invalid encryption key")
        return decrypted[len(self.SIGNATURE):]


    @staticmethod
    def encrypted_fun(data, key):
        new_data = ""
        for i in data:
            new_data += chr(ord(i) ^ key)
        return new_data


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


def packet_send_smart(entities, packet):
    path = []
    current = packet.sender
    target = packet.receiver
    while current.distance_from_earth + 150 < target.distance_from_earth:
        best_candidate = None
        max_distance = -1
        for entity in entities:
            if entity == current:
                continue
            if 0 < (entity.distance_from_earth - current.distance_from_earth) <= 150:
                if entity.distance_from_earth > max_distance:
                    best_candidate = entity
                    max_distance = entity.distance_from_earth
        if best_candidate is None:
            return "No path found"
        path.append(best_candidate)
        current = best_candidate

    current = packet.sender
    for node in reversed(path):
        packet = RelayPacket(packet, current, node)
        current = node

    transmission_attempt(packet)
    return "Message sent successfully"


network = SpaceNetwork(level=7)

earth = Earth("Earth", 0)
sat1 = Satellite("Sat1", 100, 3)
sat2 = Satellite("Sat2", 200, 6)
sat3 = Satellite("set3", 300, 2)
sat4 = Satellite("set4", 400, 5)
entities1 = [earth, sat1, sat2, sat3, sat4]

msg = EncryptedPacket("Hello from Earth!!", earth, sat4,5)

packet_send_smart(entities1, msg)

# my_packet = Packet("You're going to hit a rock!", sat1, sat2)

# sat3_to_sat4 = Packet("Hello from Earth!!", sat3, sat4)
# sat2_to_sat3 = RelayPacket(sat3_to_sat4, sat2, sat3)
# sat1_to_sat2 = RelayPacket(sat2_to_sat3, sat1, sat2)
# earth_to_sat1 = RelayPacket(sat1_to_sat2, earth, sat1)

# try:
# transmission_attempt(earth_to_sat1)
# except BrokenConnectionError:
# print("Transmission failed")
