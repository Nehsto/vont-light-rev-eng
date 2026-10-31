import asyncio
from vont import Lightbulb

MAC = "7C:DF:A1:A0:DA:C1"
UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"


def show_state(bulb):
    print(
        f"App state: power={bulb.power}, warm_mode={bulb.warm_mode}, "
        f"brightness={bulb.brightness}, color={bulb.color}",
        flush=True,
    )


async def main():
    bulb = Lightbulb(MAC, UUID)

    async def step(label, command):
        print(f"\n{label}", flush=True)
        await command
        show_state(bulb)
        await asyncio.sleep(3)

    try:
        await bulb.connect()
        print("\nAfter connecting (initial state query):", flush=True)
        show_state(bulb)
        await asyncio.sleep(3)

        await step("1. Turn on", bulb.set_power(True))
        await step("2. Switch to warm white", bulb.set_warm_mode(True))
        await step("3. Set brightness to 100%", bulb.set_brightness(100))
        await step("4. Dim to 25%", bulb.set_brightness(25))
        await step("5. Switch from warm white to red", bulb.set_color(255, 0, 0))
        await step("6. Change to green", bulb.set_color(0, 255, 0))
        await step("7. Change to blue", bulb.set_color(0, 0, 255))
        await step("8. Turn off", bulb.set_power(False))
        await step("9. Turn back on", bulb.set_power(True))
        await step("10. Return to warm white", bulb.set_warm_mode(True))
        await step("11. Set brightness to 50%", bulb.set_brightness(50))
    finally:
        if bulb.client.is_connected:
            await bulb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
