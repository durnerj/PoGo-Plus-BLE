#!/usr/bin/python3

import dbus
import dbus.mainloop.glib

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from bluez_components import *



UUID_FW_UPDATE_SERVICE = "0000fef5-0000-1000-8000-00805f9b34fb";
UUID_DEVICE_CONTROL_SERVICE = "21c50462-67cb-63a3-5c4c-82b5b9939aeb";
UUID_LED_VIBRATE_CTRL_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939aec";
UUID_BUTTON_NOTIF_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939aed";
UUID_FW_UPDATE_REQUEST_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939aef";
UUID_FW_VERSION_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939af0";
UUID_CERTIFICATE_SERVICE = "bbe87709-5b89-4433-ab7f-8b8eef0d8e37";
UUID_CENTRAL_TO_SFIDA_CHAR = "bbe87709-5b89-4433-ab7f-8b8eef0d8e38";
UUID_SFIDA_COMMANDS_CHAR = "bbe87709-5b89-4433-ab7f-8b8eef0d8e39";
UUID_SFIDA_TO_CENTRAL_CHAR = "bbe87709-5b89-4433-ab7f-8b8eef0d8e3a";
UUID_BATTERY_SERVICE = "0000180F-0000-1000-8000-00805f9b34fb";
UUID_BATTERY_LEVEL_CHAR = "00002A19-0000-1000-8000-00805f9b34fb";
UUID_CLIENT_CHARACTERISTIC_CONFIG = "00002902-0000-1000-8000-00805f9b34fb";


mainloop = None
class RowChrc(Characteristic):
    ROW_UUID = '12345678-1234-5678-1234-56789abc000'

    def __init__(self, bus, index, service, row, display):
        Characteristic.__init__(
            self, bus, index,
            self.ROW_UUID + int_to_hex(row),  # use the row number to build the UUID
            ['read', 'write'],
            service)
        self.value = [0x00, 0x00]
        self.row = row
        self.display = display

    def ReadValue(self, options):
        print('RowCharacteristic Read: Row: ' + str(self.row) + ' ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('RowCharacteristic Write: Row: ' + str(self.row) + ' ' + repr(value))
        set_display_row(self.display, self.row, value[:2])
        self.value = value[:2]


class fw_update_request_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_FW_UPDATE_REQUEST_CHAR, ['read', 'write'], service)
        self.value = [0x00, 0x00]


class fw_version_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_FW_VERSION_CHAR, ['read', 'write'], service)
        self.value = [0x00, 0x00]


class led_vibrate_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_LED_VIBRATE_CTRL_CHAR, ['read', 'write'], service)
        self.value = [0x00, 0x00]


class button_notif_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_BUTTON_NOTIF_CHAR, ['read', 'write'], service)
        self.value = [0x00, 0x00]


class sfida_commands_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_SFIDA_COMMANDS_CHAR, ['read', 'write', 'notify'], service)
        self.value = [0x00, 0x00]


class sfida_to_central_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_SFIDA_TO_CENTRAL_CHAR, ['read', 'write'], service)
        self.value = [0x00, 0x00]


class central_to_sfida_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_CENTRAL_TO_SFIDA_CHAR, ['read', 'write'], service)
        self.value = [0x00, 0x00]


class battery_level_chrc(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UUID_BATTERY_LEVEL_CHAR, ['read', 'write'], service)
        self.value = [0x00, 0x00]


class LedService(Service):
    LED_SVC_UUID = '12345678-1234-5678-1234-56789abc0010'

    def __init__(self, bus, index, display):
        Service.__init__(self, bus, index, self.LED_SVC_UUID, True)
        self.add_characteristic(RowChrc(bus, 0, self, 0, display))
        self.add_characteristic(RowChrc(bus, 1, self, 1, display))
        self.add_characteristic(RowChrc(bus, 2, self, 2, display))
        self.add_characteristic(RowChrc(bus, 3, self, 3, display))
        self.add_characteristic(RowChrc(bus, 4, self, 4, display))
        self.add_characteristic(RowChrc(bus, 5, self, 5, display))
        self.add_characteristic(RowChrc(bus, 6, self, 6, display))
        self.add_characteristic(RowChrc(bus, 7, self, 7, display))


class fw_update_service(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UUID_FW_UPDATE_SERVICE, True)
        self.add_characteristic(fw_update_request_chrc(bus, 0, self))
        self.add_characteristic(fw_version_chrc(bus, 1, self))


class device_control_service(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UUID_DEVICE_CONTROL_SERVICE, True)
        self.add_characteristic(led_vibrate_chrc(bus, 0, self))
        self.add_characteristic(button_notif_chrc(bus, 1, self))


class certificate_service(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UUID_CERTIFICATE_SERVICE, True)
        self.add_characteristic(sfida_commands_chrc(bus, 0, self))
        self.add_characteristic(central_to_sfida_chrc(bus, 1, self))
        self.add_characteristic(sfida_to_central_chrc(bus, 2, self))


class battery_service(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UUID_BATTERY_SERVICE, True)
        self.add_characteristic(battery_level_chrc(bus, 0, self))


class po_go_plus_app(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(fw_update_service(bus, 0))
        self.add_service(device_control_service(bus, 1))
        self.add_service(certificate_service(bus, 2))
        self.add_service(battery_service(bus, 3))


class LedApplication(Application):
    def __init__(self, bus, display):
        Application.__init__(self, bus)
        self.add_service(LedService(bus, 0, display))


class LedAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(LedService.LED_SVC_UUID)
        self.include_tx_power = True


class po_go_plus_advertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UUID_FW_UPDATE_SERVICE)
        self.add_service_uuid(UUID_DEVICE_CONTROL_SERVICE)
        self.add_service_uuid(UUID_CERTIFICATE_SERVICE)
        self.add_service_uuid(UUID_BATTERY_SERVICE)
        self.include_tx_power = True


def setup_display():
    display = BicolorMatrix8x8.BicolorMatrix8x8()
    display.begin()
    display.clear()
    display.write_display()
    return display


def register_ad_cb():
    """
    Callback if registering advertisement was successful
    """
    print('Advertisement registered')


def register_ad_error_cb(error):
    """
    Callback if registering advertisement failed
    """
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()


def register_app_cb():
    """
    Callback if registering GATT application was successful
    """
    print('GATT application registered')


def register_app_error_cb(error):
    """
    Callback if registering GATT application failed.
    """
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def main():
    global mainloop
    global display

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Get ServiceManager and AdvertisingManager
    service_manager = get_service_manager(bus)
    ad_manager = get_ad_manager(bus)

    # Create gatt services
#    display = setup_display()
#    app = LedApplication(bus, display)
    app= po_go_plus_app(bus)

    # Create advertisement
#    test_advertisement = LedAdvertisement(bus, 0)
    test_advertisement = po_go_plus_advertisement(bus, 0)

    mainloop = GObject.MainLoop()

    # Register gatt services
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    # Register advertisement
    ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        display.clear()
        display.write_display()


if __name__ == '__main__':
    main()

