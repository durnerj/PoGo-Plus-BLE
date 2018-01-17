#!/usr/bin/python3

import dbus
import dbus.mainloop.glib
import os
from datetime import datetime
now = datetime.now()

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from bluez_components import *

#UUID_FW_UPDATE_SERVICE =      "0000fef5-0000-1000-8000-00805f9b34fb"
UUID_DEVICE_CONTROL_SERVICE = "21c50462-67cb-63a3-5c4c-82b5b9939aeb"
UUID_LED_VIBRATE_CTRL_CHAR =  "21c50462-67cb-63a3-5c4c-82b5b9939aec"
UUID_BUTTON_NOTIF_CHAR =      "21c50462-67cb-63a3-5c4c-82b5b9939aed"
UUID_FW_UPDATE_REQUEST_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939aef"
UUID_FW_VERSION_CHAR =        "21c50462-67cb-63a3-5c4c-82b5b9939af0"
UUID_CERTIFICATE_SERVICE =    "bbe87709-5b89-4433-ab7f-8b8eef0d8e37"
UUID_CENTRAL_TO_SFIDA_CHAR =  "bbe87709-5b89-4433-ab7f-8b8eef0d8e38"
UUID_SFIDA_COMMANDS_CHAR =    "bbe87709-5b89-4433-ab7f-8b8eef0d8e39"
UUID_SFIDA_TO_CENTRAL_CHAR =  "bbe87709-5b89-4433-ab7f-8b8eef0d8e3a"
UUID_BATTERY_SERVICE =        "180f"
UUID_BATTERY_LEVEL_CHAR =     "2A19"
UUID_CLIENT_CHARACTERISTIC_CONFIG = "2902"

mainloop = None


class fw_update_request_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_FW_UPDATE_REQUEST_CHAR
        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['write'],
            service)
        self.value = 0

    def WriteValue(self, value, options):
        self.value = value
        log(self.UUID)


class fw_version_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_FW_VERSION_CHAR

        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['read'],
            service)
        self.value = 0

    def ReadValue(self, options):
        log(self.UUID)
        return [dbus.Byter(self.value)]


class led_vibrate_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_LED_VIBRATE_CTRL_CHAR

        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['write'],
            service)
        self.value = 0

    def WriteValue(self, value, options):
        self.value = value
        log(self.UUID)


class button_notif_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_BUTTON_NOTIF_CHAR

        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['notify'],
            service)
        self.value = 0
        self.notifying = False

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        log(self.UUID)

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        log(self.UUID)


class sfida_commands_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_SFIDA_COMMANDS_CHAR

        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['notify'],
            service)
        self.value = 0
        self.notifying = False

    def StartNotify(self):
        if self.notifying:
            log('Already notifying, nothing to do')
            return

        self.notifying = True
        log(self.UUID)

    def StopNotify(self):
        if not self.notifying:
            log('Not notifying, nothing to do')
            return

        self.notifying = False
        log(self.UUID)


class sfida_to_central_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_SFIDA_TO_CENTRAL_CHAR

        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['read'],
            service)
        self.value = 0

    def ReadValue(self, options):
        log("sfida read: " + repr(self.UUID))
        return [dbus.Byte(self.value)]


class central_to_sfida_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_CENTRAL_TO_SFIDA_CHAR

        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['write'],
            service)
        self.value = 0

    def WriteValue(self, value, options):
        self.value = value
        log(self.UUID)


class battery_level_chrc(Characteristic):
    def __init__(self, bus, index, service):
        self.UUID = UUID_BATTERY_LEVEL_CHAR

        Characteristic.__init__(
            self, bus, index,
            self.UUID,
            ['notify', 'read'],
            service)
        self.value = 80
        self.notifying = False

    def ReadValue(self, options):
        log('Battery Level Read: ' + repr(self.value))
        log(self.UUID)
        return [dbus.Byte(self.value)]


    def StartNotify(self):
        if self.notifying:
            log('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_battery_level()
        log(self.UUID)

    def StopNotify(self):
        if not self.notifying:
            log('Not notifying, nothing to do')
            return

        self.notifying = False
        log(self.UUID)

def log(message):
    print(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + message)
    
#class fw_update_service(Service):
#    """ Fake FW Update Service."""
#
#    def __init__(self, bus, index):
#        UUID = UUID_FW_UPDATE_SERVICE
#        Service.__init__(self, bus, index, UUID, True)
#        self.add_characteristic(fw_update_request_chrc(bus, 0, self))
#        self.add_characteristic(fw_version_chrc(bus, 1, self))


class device_control_service(Service):
    """ Fake Device Control Update Service."""

    def __init__(self, bus, index):
        UUID = UUID_DEVICE_CONTROL_SERVICE
        Service.__init__(self, bus, index, UUID, True)
        self.add_characteristic(led_vibrate_chrc(bus, 0, self))
        self.add_characteristic(button_notif_chrc(bus, 1, self))
        self.add_characteristic(fw_update_request_chrc(bus, 3, self))
        self.add_characteristic(fw_version_chrc(bus, 4, self))


class certificate_service(Service):
    """ Certificate Service."""

    def __init__(self, bus, index):
        UUID = UUID_CERTIFICATE_SERVICE
        Service.__init__(self, bus, index, UUID, True)
        self.add_characteristic(sfida_commands_chrc(bus, 0, self))
        self.add_characteristic(central_to_sfida_chrc(bus, 1, self))
        self.add_characteristic(sfida_to_central_chrc(bus, 2, self))


class battery_service(Service):
    """ Fake Battery Service."""

    def __init__(self, bus, index):
        UUID = UUID_BATTERY_SERVICE
        Service.__init__(self, bus, index, UUID, True)
        self.add_characteristic(battery_level_chrc(bus, 0, self))


class po_go_plus_app(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        #self.add_service(fw_update_service(bus, 0))
        self.add_service(battery_service(bus, 0))
        self.add_service(device_control_service(bus, 1))
        self.add_service(certificate_service(bus, 2))


class po_go_plus_advertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        #self.add_service_uuid(UUID_BATTERY_SERVICE)
        #self.add_service_uuid(UUID_DEVICE_CONTROL_SERVICE)
        #self.add_service_uuid(UUID_CERTIFICATE_SERVICE)
        #self.add_service_data("21c50462", [0x00])
        self.include_tx_power = True


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Get ServiceManager and AdvertisingManager
    gatt_properties = [
            {"Name": "Discoverable", "Set": True, "Value": False},
#            {"Name": "Alias", "Set": True, "Value": "Pokemon GO Plus"},
    ]

    service_manager = get_service_manager(bus, gatt_properties)

    ad_properties = [
            {"Name": "Discoverable", "Set": True, "Value": True},
            {"Name": "DiscoverableTimeout", "Set": True, "Value": 0},
            {"Name": "Class", "Set": False},
            {"Name": "Address", "Set": False},
            {"Name": "Name", "Set": False},
            {"Name": "Alias", "Set": True, "Value": "Pokemon GO Plus"},
            {"Name": "UUIDs", "Set": False},
            {"Name": "Modalias", "Set": False},
    ]

    ad_manager = get_advertisement_manager(bus, ad_properties)

    # Create gatt services
    app = po_go_plus_app(bus)

    # Create advertisement
    po_go_plus_ad = po_go_plus_advertisement(bus, 0)

    mainloop = GObject.MainLoop()

    # Register gatt services
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    # Register advertisement
    ad_manager.RegisterAdvertisement(po_go_plus_ad.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    log("PokeBrm Started")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        service_manager.UnregisterApplication(app.get_path())
        ad_manager.UnregisterAdvertisement(po_go_plus_ad.get_path())
        print('exit')


if __name__ == '__main__':
        main()
