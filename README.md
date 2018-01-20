# What was this before
This is a brmlab attempt at building a BLE device compatible with the
Pokemon GO Plus wristband.  We are trying to reproduce the handshake
protocol described in:

	https://hackaday.io/project/12680-pokemon-go-plus-diy

As the initial platform, we are using an nRF51 Bluefruit BLEfriend
with UART interface, connected to a Raspberry Pi.

The device is visible, but the handshake doesn't work and we aren't
sure why.

# bt sniffs

In /logs we store sniffs from pairings with pogoplus.

You can view them with wireshark. A good filter for the interesting info is: ``` (btatt.service_uuid128 == bb:e8:77:09:5b:89:44:33:ab:7f:8b:8e:ef:0d:8e:37 && (btatt.value contains 03:00:00 || btatt.value contains 05:00:00 || btatt.value contains 04:00)) ```

# Settings for BLE
execute set_btle.sh

# status
at the moment the app starts notifying ae39. but after that nothing happens. the logs indicate that after notifying the device sends something for the app with the same uuid. it seems like we have to implement the client part of bluez_gatt

# Settings for BT (btmgmt) [legacy]

It could be possible that you need to disable EDR and need to activat LE with btmgmt.
To enable LE for your chip use:

```
sudo btmgmt le on
```

To disable services we dont need like EDR power down the bluetooth and use:

```
sudo btmgmt bredr off
```
We dont know if ```sc``` and ```bondable``` should be on or not.

If you get a "busy" or "rejected" from the chip, first power down the bluetooth with:
```
sudo btmgmt power off
```

When done dont forget to power bluetooth back up:
```
sudo btmgmt power on
```
