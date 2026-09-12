<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />
<img width="1280" height="640" alt="git (1)" src="[https://github.com/user-attachments/assets/cover image](https://github.com/Adwaith585/useless_project_ORION/blob/main/assets/cover%20image.png)" />

# Anti-Productivity Sentinel 🎯

## Basic Details
### Team Name: ORION

### Team Members
- Team Lead: Adwaith S A - College of Engineering Adoor
- Member 2: Abhin J Gomez - College of Engineering Adoor

### Project Description
An autonomous desktop surveillance agent that continuously monitors your screen and webcam to prevent you from doing any actual work. If it catches you opening an IDE or holding a Pen, it instantly force-closes your productive apps and aggressively takes over your desktop with a doomscroll feed.

### The Problem (that doesn't exist)
People are way too productive and have an unhealthy obsession with getting things done. We needed a reliable system that actively forbids the user from writing code or studying in peace.

### The Solution (that nobody asked for)
We built a ruthless sentinel using a local AI vision model (Llava) and OS-level window scanners. The moment it detects any productivity, it violently `taskkill`s your IDE (deleting unsaved work) and traps your screen in an infinite, inescapable YouTube Shorts loop until you mentally surrender and hit a hidden hotkey.

## Technical Details
### Technologies/Components Used
For Software:
- Python
- PyQt5, OpenCV, pygetwindow, mss, win32api
- Ollama (Llava vision model for physical object detection)
- Windows PowerShell

### Implementation
For Software:
# Installation
First, install the backend Ollama engine directly to your operating system to enable localized AI models:
```powershell
# Windows PowerShell installation
irm https://ollama.com/install.ps1 | iex
```

Then, install the required Python packages and pull the Llava vision weights:
```bash
pip install -r requirements.txt
ollama pull llava
```

# Run
```bash
python anti_productivity_sentinel.py
```

### Project Documentation
For Software:

# Screenshots
![Sentinel Code Execution](assets/demo1.png)
*What happens after the said requirements.*

![Doomscroll YouTube Logic](assets/demo2.png)
*The QWebEngine pop-up dynamically hijacking the desktop layer with an inescapable un-closable YouTube Shorts feed.*

![Physical OpenCV Desk Pipeline](assets/demo3.png)
*Raw OpenCV debug payload confirming the pipeline successfully capturing physical workspaces and evaluating user posture via Llava.*

# Diagrams
```mermaid
graph TD
    A[Background Sentinel Starts] --> B[Capture Screen & Webcam]
    B --> C{Active Window is IDE?}
    
    C -- Yes (Hard Trigger) --> E[Violently Steal Focus]
    C -- No --> D{Motion Detected?}
    
    D -- No --> B
    D -- Yes --> F[Feed Webcam to Llava AI]
    F --> G{Analyzing: Holding Pen?}
    
    G -- "IDLE" (Slacking) --> B
    G -- "TRIGGER" (Working) --> E
    
    E --> H[taskkill IDE Processes]
    H --> I[Deploy Unskippable YouTube Shorts]
    I --> J{Ctrl+Alt+Shift+Q Pressed?}
    J -- No --> I
    J -- Yes --> K[Terminate Sentinel]
```
*Architecture flow depicting how the Anti-Productivity Sentinel seamlessly evaluates physical and digital states to aggressively prevent you from working.*

### Project Demo
# Video
<video src="assets/demo1.mp4" controls="controls" style="max-width: 100%;"></video>

> *If your markdown viewer strips native video tags, **[click here to view the raw MP4 file](assets/demo1.mp4)**.*

*Live recording demonstrating the Sentinel tracking the webcam and immediately engaging the un-closable YouTube logic.*

## Team Contributions
- Adwaith S A: Engineered the core OS-level window monitoring, PyQt5 focus-stealing mechanics, and `taskkill` logic. Curated and generated massive custom visual datasets of study environments to help fine-tune the AI's physical object detection accuracy.
- Abhin J Gomez: Integrated the Llava multi-modal vision AI via Ollama, implemented the stealth `.pyw` deployment pipeline, and rigorously built hand-labeled datasets to calibrate the precise physical motion-thresholds for the Sentinel.

---
Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)
