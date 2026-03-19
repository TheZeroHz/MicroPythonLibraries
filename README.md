# ⚡ MicroPython Libraries

<p align="center">
Lightweight • Clean • Embedded Friendly
</p>

<p align="center">
A curated collection of <b>MicroPython libraries</b> designed for<br>
<b>ESP32 • ESP32-S3 • Raspberry Pi Pico • Pico W • Other MicroPython Boards</b>
</p>

---

## 📖 Overview

This repository contains **minimal and ready-to-use MicroPython libraries** focused on **embedded development and IoT projects**.

The goal is to provide **clean, dependency-free, and memory-efficient implementations** that can easily be copied into MicroPython devices.

Most libraries are **developed and maintained by me**, while some are **inspired by existing open-source projects**. In those cases, the **original repository and features are referenced**.

---

## 📂 Repository Structure

```
MicroPythonLibraries
│
├── gsm_release
│   └── gsm
│
├── libX_release
│   └── libX
│
├── lcd_release
│   └── lcd
│
├── ............
│   └── .....
│
└── ...
```


Each **release folder** contains the **ready-to-use source code** for the corresponding library.

---

## 📦 Available Libraries

### 🔢 Keypad

Matrix keypad driver for **MicroPython**.

#### **Features**

- Support for **4×3, 4×4, and M×N matrix keypads**
- Multiple keypress detection
- Built-in **debouncing**
- **Hold key detection**
- Event listener support
- **State-machine based key tracking**


**Visit**
https://github.com/TheZeroHz/keypad

### IR Remote
Cross Platform IR Remote driver for **MicroPython**.
#### **Features**

- Support for **NEC, Sony SIRC, RC-5, RC-6, Samsung NEC, and OrtekMCE protocols**
- **Non-blocking IR signal reception**, compatible with uasyncio
- **IR code sniffing and raw signal capture** for learning remotes
- **Transmitter support** to emulate remote control buttons via IR LED
- **Repeat and hold button detection** for continuous presses
- **Configurable carrier frequency** (36–40 kHz) for transmission


**Visit**
https://github.com/peterhinch/micropython_ir

---

## 🎯 Design Philosophy

MicroPython runs on **resource-constrained hardware**, so these libraries follow strict principles:

- ⚡ Lightweight implementation
- 🧠 Minimal memory usage
- 🔧 Easy integration
- 📦 No unnecessary dependencies
- 🚀 Optimized for embedded devices

---

## 🤝 Contributing

Contributions are welcome!

You can contribute by:

- Adding new **MicroPython libraries**
- Improving existing implementations
- Fixing bugs
- Enhancing documentation

Please open an **Issue** or submit a **Pull Request**.

---

⭐ If this repository helps you, consider **starring the project**.
