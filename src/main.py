from typing import List, Dict, Optional

from lifxlan import LifxLAN, Light

import rtmidi
from rtmidi._rtmidi import MidiMessage, RtMidiIn

LIFX_VALUE_MIN = 0
LIFX_VALUE_MAX = 65535
MIDI_VALUE_MIN = 0
MIDI_VALUE_MAX = 127


def main():
    lights: Dict[str, Light] = _retrieve_lifx_lights()
    midi_in = _create_midi_connection()

    if midi_in:
        while True:
            message = midi_in.getMessage(250)  # some timeout in ms
            if message and message.isNoteOn():
                note_name: str = message.getMidiNoteName(message.getNoteNumber())
                print(f'note_name: {note_name} - velocity: {message.getVelocity()}')
                # TODO: Match the note name with the light names here, and add as many elif's as necessary
                # or as many _update_light calls for a single note as you want
                if note_name == "NOTE_NAME(C5, B4, ect)":
                    _update_light(light=lights['LIGHT_NAME'], midi_message=message)
                elif note_name == "A4":
                    _update_light(light=lights['LIGHT_NAME'], midi_message=message)
                elif note_name == "A4":
                    _update_light(light=lights['LIGHT_NAME'], midi_message=message)
                else:  # This isn't really necessary...
                    print("This note has not mapping!")


def _update_light(light: Light, midi_message: MidiMessage):
    # TODO: Probably need to fiddle with these and see what happens. They could become parameters.
    MIN_BRIGHTNESS = 500  # 0 - 65535
    BRIGHTNESS_INCREASE_SPEED = 100  # 0-?
    BRIGHTNESS_DROP_SPEED = 200  # 0-? in ms, so 1000 is 1s

    velocity = midi_message.getVelocity()
    mapped_velocity = _map_value_to_range(value=velocity,
                                          from_min=MIDI_VALUE_MIN,
                                          from_max=MIDI_VALUE_MAX,
                                          to_min=LIFX_VALUE_MIN,
                                          to_max=LIFX_VALUE_MAX)

    ########
    # TODO: We should try some different stuff here, but I'm making something up that I think will be interesting?
    ########

    # Set the color to w/e the velocity is. This could be really erratic, so maybe add duration
    # which transitions to the given color over the # of ms. Just not sure if it blocks execution.
    light.set_hue(hue=mapped_velocity, rapid=True)

    # Push the brightness up by some function of the velocity. Will need to mess with this.
    def _new_brightness(current_brightness: int):
        return current_brightness + BRIGHTNESS_INCREASE_SPEED

    light.set_brightness(brightness=_new_brightness(current_brightness=light.get_color()[2]), rapid=True)

    # Then start to lower the brightness to some min level slowly
    light.set_brightness(brightness=MIN_BRIGHTNESS, duration=BRIGHTNESS_DROP_SPEED, rapid=True)


# Values from midi seem to be 0-127, where lifx allows brightness/hue values from 0-65535
# This is a way to map the values in a linear fashion...but
# the problem is we lose a lot of color resolution doing it this way
# something to keep in mind, but it is what it is for now
def _map_value_to_range(value: int, from_min: int, from_max: int, to_min: int, to_max: int):
    # Using linear interpolation / linear mapping. I haven't tested this, so...
    from_range = (from_max - from_min)
    to_range = (to_max - to_min)
    mapped_value = (((value - from_min) * to_range) / from_range) + to_min

    return mapped_value


"""
Returns a dictionary where K->name of the light V->Light object

Reference: https://github.com/mclarkk/lifxlan
"""
def _retrieve_lifx_lights() -> Dict[str, Light]:
    num_lights = 12
    # int(sys.argv[1])...(the first arg is the script path)
    print("Discovering lights...")
    lifx_client = LifxLAN(num_lights)  # Create LifxLAN client, num_lights may be None, it's just slower that way.
    # TODO: use get_devices_by_group instead (and of course put all the drum lights in a single group)
    device_list: List[Light] = lifx_client.get_lights()
    print("\nFound {} light(s):\n".format(len(device_list)))
    lights: Dict[str, Light] = {}
    for device in device_list:
        try:
            device.set_power(True)  # Initialize every light in the group to on
            lights[device.get_label()] = device
            print(device)
        except Exception:
            pass

    return lights


"""
Reference: https://github.com/patrickkidd/pyrtmidi
"""
def _create_midi_connection() -> Optional[RtMidiIn]:
    midi_in: RtMidiIn = rtmidi.RtMidiIn()

    print("Looking for MIDI input ports...")
    ports = range(midi_in.getPortCount())
    if ports:
        print(f'{len(ports)} MIDI ports found!')
        for index, item in enumerate(ports):
            print(f'{index}) {midi_in.getPortName(item)}')

        # TODO: We can add input/prompt here to allow for picking which one to connect to if more than 1.
        print("Opening port 0!")
        midi_in.openPort(0)

        return midi_in
    else:
        print('NO MIDI INPUT PORTS!')

    return None


if __name__ == "__main__":
    main()
