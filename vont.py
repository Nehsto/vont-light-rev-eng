from bleak import BleakClient
import asyncio

class Lightbulb:
	def __init__(self, mac, uuid):
		self.mac = mac
		self.uuid = uuid
		self.client = BleakClient(self.mac)
		self.serial = 0xFFFF
		

		self.power = False
		self.warm_mode = False
		self.brightness = 100
		self.color = (0, 0, 0)

		self.state_received = asyncio.Event()

	@staticmethod
	def checksum(data: bytes) -> int:
		return (sum(data) ^ 0x33) & 0xFF

	async def connect(self):
		await self.client.connect()

		await self.client.start_notify(
			self.uuid,
			self.handle_notification
		)

		# Request all device attributes
		await self.send(0x82, b"")

		# Give the bulb time to respond
		await asyncio.sleep(0.5)
	async def disconnect(self):
		await self.client.disconnect()

	async def send(self, command: int, payload: bytes):
		length = len(payload) + 9

		packet = bytearray([
			0xAA, 0x55,
			(length >> 8) & 0xFF,
			length & 0xFF,
			(self.serial >> 8) & 0xFF,
			self.serial & 0xFF,
			0x80,
			command
		])

		packet.extend(payload)
		packet.append(self.checksum(packet))

		await self.client.write_gatt_char(
			self.UUID,
			bytes(packet),
			response=True
		)

		self.serial = (self.serial - 1) & 0xFFFF
		print("Sending:", packet.hex(" ").upper())

	async def set_power(self, on: bool):
		payload = bytes([
			0x00, 0x01,  # Attribute: power_onoff
			0x09,        # Type: BOOL
			int(on)
		])

		await self.send(0x83, payload)

	async def set_color(self, r: int, g: int, b: int):
		if not all(0 <= x <= 255 for x in (r, g, b)):
			raise ValueError("RGB values must be between 0 and 255")

		if self.warm_mode:
			await self.set_warm_mode(False)

		payload = bytes([
			0x00, 0x06,
			0x05,
			0x00, r, g, b
		])

		await self.send(0x83, payload)

	async def set_brightness(self, val: int):
		if not 0 <= val <= 100:
			raise ValueError("Brightness must be between 0 and 100")
		
		payload = bytes([
			0x00, 0x07,
			0x01,
			val
		])

		await self.send(0x83, payload)

	async def set_warm_mode(self, enabled: bool):
		payload = bytes([
			0x00, 0x0B,  # Attribute: warm_switch
			0x09,        # Type: BOOL
			int(enabled)
		])

		await self.send(0x83, payload)
		self.warm_mode = enabled

	def handle_notification(self, sender, data):
	# Validate Vont packet header and command
		if len(data) < 9 or data[:2] != b'\xAA\x55' or data[7] != 0x82:
			return

		payload = data[8:-1]
		i = 0

		while i + 3 <= len(payload):
			index = int.from_bytes(payload[i:i+2], "big")
			dtype = payload[i+2]
			i += 3

			# Types used by the attributes we're tracking
			sizes = {0x09: 1, 0x01: 1, 0x05: 4}

			if dtype not in sizes:
				break

			size = sizes[dtype]
			if i + size > len(payload):
				break

			value = payload[i:i+size]
			i += size

			if index == 1:
				self.power = bool(value[0])
			elif index == 6:
				self.color = tuple(value[1:4])
			elif index == 7:
				self.brightness = value[0]
			elif index == 11:
				self.warm_mode = bool(value[0])