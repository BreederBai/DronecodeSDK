#!/usr/bin/env python

import pydronecode_sdk
import time
import threading


def listen_to_position(telemetry, should_exit):
    """Just poll position and print it."""
    while not should_exit.is_set():
        position = telemetry.position()
        print("Lat: {}, lon: {}, alt: {}".format(
            position.latitude_deg,
            position.longitude_deg,
            position.relative_altitude_m))
        time.sleep(1)


def main():
    """Connect, takeoff, and land again."""
    dc = pydronecode_sdk.DronecodeSDK()

    dc.add_udp_connection(14540)
    # We need to wait to make sure a system connects in the meantime.
    time.sleep(2)

    if len(dc.system_uuids()) == 0:
        print("No system found")
        sys.exit(1)

    if len(dc.system_uuids()) >= 2:
        print("More than one system found")
        sys.exit(1)

    action = pydronecode_sdk.Action(dc.system())
    telemetry = pydronecode_sdk.Telemetry(dc.system())

    # We use an event to tell the thread to stop again.
    should_exit = threading.Event()
    t = threading.Thread(target=listen_to_position,
                         args=(telemetry, should_exit))
    t.start()

    action.set_takeoff_altitude(1.0)

    print("Arming...", end="")
    action.arm()
    print("done.")

    print("Taking off...", end="")
    action.takeoff()
    print("done.")

    # Let it hover briefly.
    time.sleep(5)

    print("Landing...", end="")
    action.land()
    print("done.")

    print("Exiting...", end="")
    should_exit.set()
    t.join()
    print("done.")


if __name__ == '__main__':
    main()
