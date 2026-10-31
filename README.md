# Bluetooth Lightbulb Controller

A simple local web app to turn a Vont lightbulb on or off, switch warm light, adjust brightness, and choose a color.

## Setup

On a computer with Python 3 and Bluetooth, open a terminal in the project folder. Set `MAC` and `UUID` in `app.py` to match your bulb, then create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the requirements and start the app:

```bash
python -m pip install -r requirements.txt
python app.py
```

Keep the terminal running and open [http://localhost:8080](http://localhost:8080) on that computer to control the lightbulb. The bulb must be powered and within Bluetooth range.

To use a phone on the same Wi-Fi network, open `http://<computer-ip>:8080` using the computer's local IP address. Press **Ctrl+C** in the terminal to stop the app.
