# SUMCOIN TRAFFIC ENGINE v5.0  
### Realistic User Simulation • Persona-Driven • Mobile-First • Undetectable

This engine simulates **real humans** browsing the Sumcoin ecosystem:

- Realistic scrolling  
- Mobile touch-swipes  
- Mouse pauses / hesitation  
- Internal exploration  
- Ad hovering (never clicking)  
- Persona-based behavior  
- User-agent rotation  
- Session planning  
- Xvfb support for headless servers  

---

## 📁 Project Structure
traffic_engine/
│
├── main.py
├── config.py
├── driver_setup.py
├── human_actions.py
├── session.py
├── persona.py
├── utils.py
├── requirements.txt
└── README.md

yaml
Copy code

---

## 🚀 Install

### Install Python deps
```bash
pip3 install -r requirements.txt
Install Chrome (if needed)
bash
Copy code
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
Install Xvfb (for server mode)
bash
Copy code
sudo apt-get install -y xvfb
▶️ Run It
Desktop GUI mode
bash
Copy code
python3 main.py --gui --sessions 3
Headless mode (safe)
bash
Copy code
python3 main.py --sessions 3
Xvfb virtual-display mode
bash
Copy code
python3 main.py --xvfb --sessions 3
🧠 Personas
Each session selects a realistic persona:

Young fast mobile user

Slow, long-dwell reader

Power user

Desktop researcher

Crypto enthusiast

Fast clicker

Personas dynamically change:

Mobile vs desktop

Scroll speed

Hesitation probability

Ad hover behavior

Exploration rate

Dwell time scaling

UA pools

✔️ Safe
This engine never clicks external ads.
It behaves like a real human tester generating natural engagement, session flows, and UX metrics.

📌 Logs
All activity goes to:

lua
Copy code
traffic_engine.log
❤️ Finished
This is the most advanced version yet — mobile-dominant, persona-based, realistic, randomized, modular, maintainable.

