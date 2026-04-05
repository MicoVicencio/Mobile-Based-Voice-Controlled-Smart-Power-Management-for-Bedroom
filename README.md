# 🏠 Mobile-Based Voice-Controlled Smart Power Management for Bedroom

> **System #02 · Smart Home IoT**
> Capstone Project — Bachelor of Science in Computer Science
> Cainta Catholic College

---

## 📖 Overview

The **Mobile-Based Voice-Controlled Smart Power Management for Bedroom** is a smart home prototype that automates bedroom appliances — lights, lamps, air conditioners, and televisions — through voice commands and manual mobile controls. Spoken commands are converted to text via the Google Speech Recognition API, sent to Firebase, and executed by Arduino-controlled relays, all while a web dashboard monitors temperature and device states.

---

## ✨ Features

- **Voice Command Control** — Users speak commands that are processed by the Google Speech Recognition API and relayed to the hardware.
- **Manual Mobile Switches** — The Android app also provides tap-to-toggle controls for users who prefer manual operation.
- **Temperature Monitoring** — Arduino reads room temperature sensor data and streams it to Firebase for real-time display.
- **Firebase Real-Time Sync** — Cloud database bridges the mobile app, Python backend, and IoT hardware seamlessly.
- **Web Monitoring Dashboard** — Admins and users can view live device statuses and environmental readings from any browser.

---

## 🛠️ Technologies Used

| Category        | Technologies                                                    |
|-----------------|-----------------------------------------------------------------|
| **Languages**   | Python, C++, Java, HTML, CSS, JavaScript                        |
| **Database**    | Firebase Realtime DB                                            |
| **APIs & Cloud**| Firebase, Google Speech Recognition API                         |
| **Hardware**    | Arduino, Temperature Sensor, Relay Module                       |

---

## 🏗️ System Architecture

```
[Voice Command (User)]
         │
         ▼
[Google Speech Recognition API]
         │
         ▼
[Android Mobile App (Java)]
         │
         ▼
[Firebase Realtime Database]
    ┌────┴────┐
    ▼         ▼
[Python    [Web Dashboard]
 Backend]
    │
    ▼
[Arduino + Relay Module]
    │
    ▼
[Bedroom Appliances]
(Lights / Lamp / AC / TV)
         │
[Temperature Sensor] ──► [Firebase] ──► [Dashboard Display]
```

---

## ⚙️ How It Works

1. The user speaks a command (e.g., *"Turn on the lights"*) into the Android app.
2. Google Speech Recognition API converts speech to text.
3. The Android app sends the parsed command to Firebase Realtime Database.
4. The Python backend listens to Firebase and translates commands into relay signals.
5. Arduino reads the relay commands and switches the corresponding appliance ON or OFF.
6. The Arduino simultaneously reads the temperature sensor and uploads readings to Firebase.
7. The web dashboard displays all device states and temperature data in real time.

---

## 🗣️ Supported Voice Commands (Examples)

| Command | Action |
|---------|--------|
| "Turn on the lights" | Activates bedroom lights |
| "Turn off the lamp" | Deactivates the lamp |
| "Turn on the air conditioner" | Activates the AC |
| "Turn off the television" | Deactivates the TV |

---

## 📋 Prerequisites

- Python 3.x
- Arduino IDE
- Android Studio (for building the mobile app)
- Firebase account (Realtime Database enabled)
- Google Cloud account (Speech-to-Text API enabled)
- Arduino board (e.g., Uno/Mega)
- Relay module (4-channel or more)
- Temperature sensor (e.g., DHT11/DHT22)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/smart-power-home.git
cd smart-power-home
```

### 2. Configure Firebase
- Create a Firebase project and enable Realtime Database.
- Add your `google-services.json` to the Android app directory.
- Update the Firebase config in the Python backend.

### 3. Enable Google Speech API
- Enable the **Cloud Speech-to-Text API** in your Google Cloud Console.
- Download API credentials and configure them in the Android app.

### 4. Flash the Arduino
- Open `/hardware/smart_home.ino` in Arduino IDE.
- Install required libraries: `DHT`, `Firebase-ESP-Client`.
- Upload to your Arduino board.

### 5. Run the Python Backend
```bash
pip install -r requirements.txt
python listener.py
```

### 6. Build & Run the Android App
- Open the `/android` directory in Android Studio.
- Sync Gradle and build the project.
- Deploy to an Android device or emulator.

### 7. Open the Web Dashboard
- Navigate to `/web` and open `index.html` in a browser, or deploy to a web server.

---

## 👥 Team

| Name | Role |
|------|------|
| Alvarado, John Zymond D. | BSCS Student |
| Arado, Nemuel Adrian | BSCS Student |
| Bañas, JhonPaul B. | BSCS Student |
| Gabilo, Carl Allen R. | BSCS Student |
| Vicencio, Mico D. | Group Leader / Main Programmer |

---

## 🏫 Institution

**Cainta Catholic College**
Bachelor of Science in Computer Science — BSCS Tech Expo

---

*Built with ❤️ by BSCS Students of Cainta Catholic College*
