import asyncio
import tkinter as tk
from bleak import BleakScanner, BleakClient
import threading

HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

class HeartRateMonitorApp(tk.Tk):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.title("Heart Rate Monitor")
        self.geometry("300x100")
        self.label = tk.Label(self, text="Searching for Polar H10...", font=("Helvetica", 16))
        self.label.pack(padx=20, pady=20)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    async def update_heart_rate(self, sender, data):
        heart_rate = int(data[1])
        self.label.config(text=f"Heart Rate: {heart_rate}")

    async def connect_to_device(self, address, uuid):
        self.client = BleakClient(address)
        await self.client.connect()
        await self.client.start_notify(uuid, self.update_heart_rate)
        self.label.config(text="Connected. Receiving data...")
        await asyncio.Future()  # Run indefinitely until cancelled

    async def find_device_and_run(self):
        devices = await BleakScanner.discover()
        for device in devices:
            if device.name and "Polar H10" in device.name:
                self.label.config(text="Polar H10 found! Connecting...")
                await self.connect_to_device(device.address, HEART_RATE_UUID)
                break
        if not hasattr(self, 'client') or not self.client.is_connected:
            self.label.config(text="No Polar H10 found. Please try again.")

    def on_close(self):
        print("Closing application...")
        if hasattr(self, 'client') and self.client.is_connected:
            # Disconnect the BLE client
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
        # Stop the asyncio event loop
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.destroy()


def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    asyncio_loop = asyncio.new_event_loop()
    app = HeartRateMonitorApp(asyncio_loop)

    # Run the asyncio event loop in a separate thread
    threading.Thread(target=run_asyncio_loop, args=(asyncio_loop,), daemon=True).start()

    # Schedule the asyncio tasks from the asyncio loop
    asyncio.run_coroutine_threadsafe(app.find_device_and_run(), asyncio_loop)

    app.mainloop()

if __name__ == "__main__":
    main()
