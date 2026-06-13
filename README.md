![PyPI Version](https://img.shields.io/pypi/v/RPi.GPIO?label=PyPI&style=flat&logo=raspberrypi&color=green)
![Project Stars](https://img.shields.io/github/stars/IliyaTrishechkin/pi-led-animations?label=Stars&style=flat&color=gold)
![Forks](https://img.shields.io/github/forks/IliyaTrishechkin/pi-led-animations?label=Forks&style=flat&color=orange)
![Last Commit](https://img.shields.io/github/last-commit/IliyaTrishechkin/pi-led-animations?label=Last%20Commit&style=flat&color=blue)
![License](https://img.shields.io/github/license/IliyaTrishechkin/pi-led-animations?label=License&style=flat&color=brightgreen)
![Repo Size](https://img.shields.io/github/repo-size/IliyaTrishechkin/pi-led-animations?label=Repo%20Size&style=flat&color=success)
![GitHub Release](https://img.shields.io/github/v/release/IliyaTrishechkin/pi-led-animations?style=flat)

# pi-led-animations

A Python tool for Raspberry Pi that controls a custom 9-LED board through GPIO pins and provides multiple LED animation modes.  
Now with **physical button** (GPIO 14) to cycle through animations and a **Telegram bot** for remote control.

---

# 🖥 Hardware Platform

This project was developed and tested on a **Raspberry Pi Model B Revision 2.0** using the standard **26-pin P1 GPIO header**.

**Target platform:** Raspberry Pi Model B Rev 2.0 running Raspberry Pi OS with Python 3 and the `RPi.GPIO` library.

The software uses BCM GPIO numbering:

```python
GPIO.setmode(GPIO.BCM)

## P1 Header Pinout

```text
P1:
   3V3 (1)  (2) 5V
 GPIO2 (3)  (4) 5V
 GPIO3 (5)  (6) GND
 GPIO4 (7)  (8) GPIO14
   GND (9)  (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8
   GND (25) (26) GPIO7
```

## GPIO Pins Used

| Component | BCM GPIO | Physical Pin |
|-----------|-----------|---------------|
| LED 1 | GPIO4 | 7 |
| LED 2 | GPIO17 | 11 |
| LED 3 | GPIO18 | 12 |
| LED 4 | GPIO27 | 13 |
| LED 5 | GPIO22 | 15 |
| LED 6 | GPIO23 | 16 |
| LED 7 | GPIO24 | 18 |
| LED 8 | GPIO25 | 22 |
| LED 9 | GPIO7 | 26 |
| Button | GPIO14 | 8 |

## 🔌 Hardware Setup & Architecture

Each LED is connected to a dedicated GPIO pin through a **330 Ω current-limiting resistor** and shares a common ground connection.

A physical push button is connected between **GPIO 14** and **GND**. The internal pull-up resistor of the GPIO pin is enabled, so pressing the button pulls the pin **LOW**.

### Complete 9-LED + Button Wiring Diagram

```text
Raspberry Pi                     LED_BOARD + BUTTON

┌──────────────┐
│ GPIO 4  ├────[ 330 Ω ]────(✦ LED 1 )───┐
│ GPIO 17 ├────[ 330 Ω ]────(✦ LED 2 )───┤
│ GPIO 18 ├────[ 330 Ω ]────(✦ LED 3 )───┤
│ GPIO 27 ├────[ 330 Ω ]────(✦ LED 4 )───┤
│ GPIO 22 ├────[ 330 Ω ]────(✦ LED 5 )───┼───► GND (Common Ground)
│ GPIO 23 ├────[ 330 Ω ]────(✦ LED 6 )───┤
│ GPIO 24 ├────[ 330 Ω ]────(✦ LED 7 )───┤
│ GPIO 25 ├────[ 330 Ω ]────(✦ LED 8 )───┤
│ GPIO 7  ├────[ 330 Ω ]────(✦ LED 9 )───┘
│         │
│ GPIO 14 ├───────────────( Button )─────┘
└──────────────┘
```

When the button is pressed, the current animation stops and the next animation mode (in the order: `ladder → snake → ping_pong → static → reverse_blink → blink → back to ladder`) starts automatically.

## 📷 Hardware Photos

### Breadboard LED Assembly

![Breadboard LED Assembly](images/breadboard_led_board.jpg)

*Custom 9-LED board assembled on a breadboard with individual current-limiting resistors.*

### Raspberry Pi GPIO Connection

![Raspberry Pi GPIO Connection](images/raspberry_pi_gpio_connection.jpg)

*LED board connected to the Raspberry Pi GPIO header.*

## 🎞 Animation Demonstrations

### Ladder Animation

![Ladder Animation](gifs/ladder.gif)

### Snake Animation

![Snake Animation](gifs/snake.gif)

### Ping Pong Animation

![Ping Pong Animation](gifs/ping_pong.gif)

### Blink Animation

![Blink Animation](gifs/blink.gif)

### Reverse Blink Animation

![Reverse Blink Animation](gifs/reverse_blink.gif)

### Static Mode

![Static Mode](gifs/static.gif)

## 📦 Installation

### Install Dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r requirements.txt
```

`requirements.txt` includes:

- `RPi.GPIO`
- `python-telegram-bot`
- `python-dotenv`
- and their dependencies

### Download the Project

Clone the repository:

```bash
git clone https://github.com/IliyaTrishechkin/pi-led-animations.git
cd pi-led-animations
```

Or download the ZIP archive directly from GitHub.

---

## 🚀 Running the Program

### 1. Command-line Interface (CLI)

```bash
python3 LED_animations.py [options]
```

Example:

```bash
python3 LED_animations.py -type snake -time 0.3 -len 3
```

The CLI also handles the physical button automatically – you don't need to add any extra options.

### 2. Telegram Bot (Remote Control)

The bot runs independently and controls the same LED animations.

#### Setup

1. Create a bot via **@BotFather** on Telegram.
2. Get the API token (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`).
3. Create a `.env` file in the project root:

```bash
nano .env
```

Fill it with:

```env
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_ID=your_telegram_user_id
```

> Your Telegram user ID can be obtained from **@userinfobot**.

4. Run the bot:

```bash
python3 tg_bot.py
```

The bot will start polling. Send `/start` to your bot on Telegram.

#### Bot Commands and Workflow

- `/start` – shows the main menu with buttons for all animation modes.

- Tap any animation button to enter the parameter editing menu, where you can adjust:

  - `time` – delay in seconds (`float`)
  - `len` – segment length for `snake` and `ping_pong` (`integer ≤ 8`)
  - `quantity` – number of blinks per LED for blink modes

- After editing, press **"Run code -->"** to start the animation in a background thread.

- From the main menu, you can also press **"Stop animation"** to stop any running animation.

The bot also reports errors to the admin via private message.

---

## ❓ CLI Help

```bash
python3 LED_animations.py -help
```

Output:

```text
Options:
  -help               Show this help message
  -time <float>       Set timeout delay (default: 0.5)
  -len <int>          Set length (default: 1, max: 8)
  -quantity <int>     Set number of flashes for blink modes (default: 5)
  -type <str>         Set LED type (default: ladder)
                      [ladder, snake, ping_pong, static, reverse_blink, blink]
```

---

## ⚙ Command Line Arguments (CLI)

### `-type`

Animation mode.

Available modes:

| Mode | Description |
|--------|-------------|
| `ladder` | LEDs turn on one by one, then off in reverse order |
| `snake` | Moving illuminated segment (circular) |
| `ping_pong` | Moving segment bouncing between ends |
| `static` | All LEDs constantly ON |
| `reverse_blink` | Blinks each LED from last to first |
| `blink` | Blinks each LED from first to last |

### `-time`

Delay between animation steps in seconds (`float`).

Default: `0.5`

### `-len`

Used only by `snake` and `ping_pong`.

Length of the illuminated segment (`1..8`).

Default: `1`

### `-quantity`

Used only by `blink` and `reverse_blink`.

Number of flashes per LED.

Default: `5`

---

## 🎨 Animation Modes (Examples)

### Ladder

```bash
python3 LED_animations.py -type ladder -time 0.4
```

### Snake

```bash
python3 LED_animations.py -type snake -time 0.4 -len 3
```

### Ping Pong

```bash
python3 LED_animations.py -type ping_pong -time 0.4 -len 3
```

### Static

```bash
python3 LED_animations.py -type static
```

### Blink

```bash
python3 LED_animations.py -type blink -time 0.4 -quantity 3
```

### Reverse Blink

```bash
python3 LED_animations.py -type reverse_blink -time 0.4 -quantity 3
```

---

## 🛑 Stopping the Program

- **CLI version:** Press `Ctrl+C`. GPIO cleanup is performed automatically.

- **Telegram bot:** Tap the **"Stop animation"** button.

- **Physical button:** Pressing the button while an animation is running stops it and switches to the next animation mode automatically.

---

## 📂 Project Structure

```text
pi-led-animations/
│
├── LED_animations.py       # Main LED control, CLI, button handler
├── tg_bot.py               # Telegram bot for remote control
├── requirements.txt        # Python dependencies
├── .env                    # Environment file (not committed, create yourself)
├── LICENSE                 # MIT License
├── README.md
│
├── images/
│   ├── breadboard_led_board.jpg
│   └── raspberry_pi_gpio_connection.jpg
│
└── gifs/
    ├── ladder.gif
    ├── snake.gif
    ├── ping_pong.gif
    ├── blink.gif
    ├── reverse_blink.gif
    └── static.gif
```

---

## 📝 License

This project is released under the **MIT License**.