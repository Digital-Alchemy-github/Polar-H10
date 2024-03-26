import asyncio
from bleak import BleakScanner, BleakClient

# The standard heart rate measurement UUID
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

async def notification_handler(sender, data):
    """
    Handle receiving notification from the heart rate measurement characteristic.
    """
    heart_rate = int(data[1])
    print(f"Heart Rate: {heart_rate}")

async def run_ble_client(address, uuid):
    async with BleakClient(address) as client:
        connected = client.is_connected
        print(f"Connected: {connected}")
        await client.start_notify(uuid, notification_handler)
        print("Subscribed to heart rate notifications. Receiving data...")
        await asyncio.sleep(30)
        print("Unsubscribing and disconnecting...")
        await client.stop_notify(uuid)

async def run():
    print("Scanning for Polar H10...")
    devices = await BleakScanner.discover()
    polar_h10_address = None
    for device in devices:
        print(f"Found device: {device.name}, Address: {device.address}")
        if device.name and "Polar H10" in device.name:
            polar_h10_address = device.address
            print(f"Found Polar H10: {device.name}, Address: {device.address}")
            break  # Stop scanning once the first Polar H10 is found
    
    if polar_h10_address:
        await run_ble_client(polar_h10_address, HEART_RATE_MEASUREMENT_UUID)
    else:
        print("No Polar H10 found.")

# Start the process
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
