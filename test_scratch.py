import asyncio
from vont import Lightbulb

MAC = "7C:DF:A1:A0:DA:C1"
UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

async def main():
	bulb = Lightbulb(MAC, UUID)

	try:
		await bulb.connect()

		print("Power:", bulb.power)
		print("Warm mode:", bulb.warm_mode)
		print("Brightness:", bulb.brightness)
		print("Color:", bulb.color)
		
		await bulb.set_warm_mode(False)   # Warm color
		await bulb.set_brightness(100)

		await asyncio.sleep(2)
		await bulb.set_color(255, 0, 0)  # Switch to RGB cyan

		await asyncio.sleep(2)
		await bulb.set_warm_mode(True)   # Warm color
		await bulb.set_brightness(50)

	finally:
		if bulb.client.is_connected:
			await bulb.disconnect()


asyncio.run(main())