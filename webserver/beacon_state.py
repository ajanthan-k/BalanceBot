class BeaconState:
    def __init__(self):
        self.beacon_on = False

    def set_beacon_on(self, value: bool):
        self.beacon_on = value

    def get_beacon_on(self):
        return self.beacon_on

def get_beacon_state():
    return BeaconState()
