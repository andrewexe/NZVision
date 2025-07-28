# NZVision 🚀🎥🎵

**NZVision** is an intelligent desktop utility that captures **live video and audio** from your **NZXT HD60** or any capture device and transforms it into **scene-aware insights** and **transcribed dialogue**. Whether you're debugging game logic, archiving commentary, or building real-time analytics, NZVision gives you developer-grade visibility into what your gameplay or stream is doing.

---

## ✨ Features

| Module                                  | Description                                                                                     |
| --------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 📸 **Video Scene Capture**              | Grab high-resolution frames directly from OBS Virtual Camera or NZXT devices                    |
| 🎤 **Audio Transcription**              | Real-time voice-to-text using OpenAI Whisper (great for commentary, dialogue analysis)          |
| 📅 **Time-tagged Metadata**             | Automatically names files with clean timestamps for versioning/debugging                        |
| ⌨ **Hotkey Driven UX**                  | Intuitive global hotkeys for hands-off control                                                  |
| 🤖 **AI-Powered Insights** *(optional)* | Hook into GPT/Claude for scene classification, sentiment tagging, or post-session summarization |

---

## 🚀 Use Case Examples

* **Scene Classification Engine**: Take screenshots on action events (kills, boss phases, transitions) and classify them into labeled categories
* **Post-Match Analysis**: Transcribe team comms, clip strategic moments, and review what went wrong (or right)
* **AI Coaching Bot**: Combine screenshots + transcriptions + GPT to generate advice, summaries, or hype reels
* **Streamer Enhancement**: Use hotkeys to log events, auto-transcribe speech, or trigger voice recognition overlays

---

## 📚 How It Works

1. Captures live **video frames** from your selected video device (default: OBS Virtual Camera)
2. Records high-quality **audio input** from your capture card (e.g., NZXT HD60)
3. Transcribes voice data into readable text using **OpenAI Whisper**
4. Saves results (screenshots, WAV files, transcripts) in a `~/Problems` folder

---

## ⌨ Hotkeys

| Hotkey             | Action                                               |
| ------------------ | ---------------------------------------------------- |
| `Ctrl + Shift + S` | Capture a screenshot from the video feed             |
| `Ctrl + Shift + R` | Start/Stop audio recording and generate a transcript |
| `Ctrl + Shift + D` | List available audio input devices                   |
| `Ctrl + Shift + Q` | Exit the program gracefully                          |

---

## 🚧 Setup

### 1. Install Tesseract (if OCR planned later)

* macOS: `brew install tesseract`
* Windows: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)

### 2. Clone & Install

```bash
git clone https://github.com/your-username/nzvision.git
cd nzvision
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

```bash
export OPENAI_API_KEY=your-key-here
```

### 4. Run the capture tool

```bash
python capture.py
```

---

## 📖 File Outputs

All output files are saved to your `~/Problems/` folder:

* `screenshot_YYYY-MM-DD_HH-MM-SS.png` → Raw video frame
* `debug_audio_YYYY-MM-DD_HH-MM-SS.wav` → Uncompressed audio
* `transcript_YYYY-MM-DD_HH-MM-SS.txt` → Whisper-generated text

---

## 🧪 Ideas for Extensions

* Plug into an ML model for **real-time scene labeling**
* Add sentiment analysis to audio (rage vs. hype)
* Train an SVM or CNN on captured frames for automatic highlight detection
* Auto-upload outputs to a cloud dashboard for review
* Summarize entire gameplay sessions with GPT-4 or Claude

---

## 📄 License

MIT License © 2025 Andrew Huang
