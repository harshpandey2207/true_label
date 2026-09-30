<div align="center">
  <h1>🏷️ True Label</h1>
  <h3>AI-Powered Legal Metrology & AR Compliance Scanner</h3>
  <p>Ensuring consumer trust and regulatory compliance through instant computer vision.</p>
</div>

---

## 🚀 Overview
**True Label** is an advanced AI engine designed to instantly verify packaged commodities against Legal Metrology Rules. By combining deep-learning OCR with Augmented Reality (AR) overlays, True Label allows consumers, inspectors, and manufacturers to scan a product and immediately see if it contains all legally mandated declarations (MRP, Manufacturing Date, Net Quantity, Storage Instructions, etc.).

## 🔗 Live Demo
**Test the app directly in your browser:** [True Label Web App](https://true-label-jade.vercel.app/)

> ⚠️ **Architecture Notice (Live Demo)**
> The core open-source architecture of True Label utilizes **PaddleOCR (PP-OCRv4)** to handle complex metrology extraction and AR bounding box geometry. Due to the high compute constraints (0.1 vCPU limits) of our free-tier cloud hosting (which caused 2-5 minute processing delays for deep learning math), this live web demo temporarily routes inference through a lightweight cloud API to ensure fast, 3-second evaluation for the judges. 
> *You can view our full open-source PaddleOCR fallback implementation in `backend/app/services/ai_engine/metrology_engine.py`.*

## ✨ Key Features
- **Instant Label Analysis:** Automatically extracts text from curved bottles, boxes, and tubes.
- **AR Bounding Boxes:** Projects compliant (green) and non-compliant (red) highlights directly onto the product using dynamic focal geometry.
- **Rule-Based Compliance Engine:** Verifies the presence of mandatory fields and checks for misleading formatting.
- **Cross-Platform:** Built with Flutter, running seamlessly on Web, Android, and iOS.

## 🛠️ Technology Stack
- **Frontend:** Flutter, Dart
- **Backend:** Python, FastAPI, Uvicorn
- **Computer Vision & AI:** OpenCV, PaddleOCR (Open Source), NumPy
- **Deployment:** Vercel (Frontend), Render (Backend)

## 🧠 How It Works (The Pipeline)
1. **Image Capture:** The Flutter app captures an image of the product and auto-downscales it for bandwidth efficiency.
2. **AI Text Detection:** The image is processed by the AI engine to detect text polygons and extract strings across curved/angled surfaces.
3. **Metrology Engine:** The parsed text is run against a strict regex and keyword ruleset to classify declarations (e.g., matching "Store below 25C" to the *STORAGE* tag).
4. **AR Rendering:** The backend calculates precise focal geometry to scale the bounding boxes back to the original image dimensions, sending them to the Flutter app to render as smart AR overlays.

## 💻 Local Setup (Backend)
To run the full open-source PaddleOCR engine locally on your own hardware:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

