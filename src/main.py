import sys

from lifxlan import LifxLAN, Light

import rtmidi


def main():
    num_lights = 12
    if len(sys.argv) != 2:
        print("\nDiscovery will go much faster if you provide the number of lights on your LAN:")
        print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
    else:
        num_lights = int(sys.argv[1])

    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.
    print("Discovering lights...")
    lifx = LifxLAN(num_lights)

    # get devices
    devices = lifx.get_lights()
    print("\nFound {} light(s):\n".format(len(devices)))
    for d in devices:
        try:
            print(d)
        except Exception:
            pass

    right: Light = Light("d0:73:d5:20:e4:c6", "10.0.0.27")

    right.set_power(True)

    midiin = rtmidi.RtMidiIn()

    def print_message(midi):
        if midi.isNoteOn():
            print('ON: ', midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
        elif midi.isNoteOff():
            print('OFF:', midi.getMidiNoteName(midi.getNoteNumber()))
        elif midi.isController():
            print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())

    ports = range(midiin.getPortCount())
    if ports:
        for i in ports:
            print(midiin.getPortName(i))
        print("Opening port 0!")
        midiin.openPort(0)
        while True:
            m = midiin.getMessage(250)  # some timeout in ms
            if m and m.isNoteOn():
                right.set_brightness(m.getVelocity() * 512)
                print(f'{m.getVelocity()} {m.getMidiNoteName(m.getNoteNumber())}')
                # print_message(m)
    else:
        print('NO MIDI INPUT PORTS!')


if __name__ == "__main__":
    main()
