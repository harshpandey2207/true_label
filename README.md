<div align="center">
  <img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <h1>🔎 True Label</h1>
  <h3>AI-Powered Legal Metrology & AR Compliance Scanner</h3>
  <p>Ensuring consumer trust and strict regulatory compliance through instant computer vision.</p>
</div>

---

## 🚀 Live Demo
**Test the app directly in your browser:** [True Label Web App](https://true-label-jade.vercel.app/)

> ⚠️ **Architecture Notice (Live Demo)**
> The core open-source architecture of True Label utilizes **PaddleOCR (PP-OCRv4)** alongside traditional feature-matching algorithms (like SIFT/ORB) to handle complex metrology extraction. Due to the high compute constraints of our free-tier cloud hosting, this live web demo temporarily routes inference through a lightweight cloud API to ensure fast evaluation. 

## 📋 Overview
**True Label** is an advanced AI engine designed to instantly verify packaged commodities against the **Legal Metrology (Packaged Commodities) Rules, 2011**. 

By combining deep-learning OCR with dynamic rule-matching algorithms, True Label allows consumers, inspectors, and manufacturers to scan a product and immediately verify if it contains all legally mandated declarations (MRP, Manufacturing Date, Net Quantity, etc.) based on its strict legal product category.

## ✨ Key Features
- **Dynamic Legal Metrology Act Rules:** Enforces distinct mandatory tags based on 5 strict product categories:
  - *General Packaged Commodities*
  - *Food & Beverages (FSSAI norms)*
  - *Electronics & Appliances (BIS/E-Waste)*
  - *Cosmetics, Ointments & Pharma Goods (Drugs & Cosmetics Act)*
  - *Apparel & Textiles*
- **Automated PDF Reports:** Generates official A4 Legal Metrology E-Notices and Compliance Reports natively on the client, appending high-res proof images directly to the document.
- **60FPS Spatial Map Optimizations:** The Admin Dashboard features an interactive choropleth heatmap of India optimized with decoupled dual-canvas caching and spatial debouncing for absolute 60FPS interactivity.
- **AI Text Detection:** Extracts text from curved bottles, boxes, and tubes using robust optical character recognition and SIFT feature tracking, ignoring background noise.
- **Cross-Platform UI:** Built with Flutter, running seamlessly and responsively on Web, Android, and iOS.

## 🧠 Production Architecture & AR Engine
For our final production environment, True Label heavily relies on industry-standard spatial computing and computer vision algorithms:
* **Hybrid Computer Vision (SIFT & PaddleOCR):** 
  We utilize a hybrid approach. Deep Learning (PaddleOCR's CNNs/RNNs) extracts the raw text from complex curves, while Scale-Invariant Feature Transform (**SIFT**) and ORB algorithms anchor the text to specific physical features on the product packaging. This ensures the bounding boxes don't jitter when the camera moves.
* **Native Spatial Computing (ARCore & ARKit):** 
  While the Web Demo uses a custom focal geometry fallback, the production mobile applications utilize **ARCore (Android)** and **ARKit (iOS)**. These native frameworks provide True Label with real-time 3D depth mapping and planar tracking, allowing our green and red compliance bounding boxes to stick perfectly to the physical product in real physical space.

## 🛠️ Technology Stack
- **Frontend:** Flutter, Dart, `pdf` / `printing`
- **Mobile AR Integration:** ARCore (Android) / ARKit (iOS)
- **Backend:** Python, FastAPI, Uvicorn
- **Database:** PostgreSQL (SQLAlchemy, psycopg2)
- **Computer Vision & AI:** OpenCV (SIFT/ORB), PaddleOCR, NumPy
- **Deployment:** Vercel (Frontend), Render (Backend & DB)

## 🔄 How It Works (The Pipeline)
1. **Image Capture:** The Flutter app captures multiple images of the product packaging and downscales them for bandwidth efficiency.
2. **Backend AI Analysis:** The images are processed by the FastAPI backend using OpenCV (SIFT) and PaddleOCR to detect text polygons and extract strings.
3. **Database Rule-Matching:** The parsed text is run against a strict regex algorithm, then cross-referenced dynamically against the PostgreSQL database containing the 2011 Legal Metrology rules.
4. **Actionable Compliance:** Missing mandatory declarations are immediately flagged in the Inspector dashboard, and a downloadable PDF E-Notice is dispatched.

## 💻 Local Setup (Backend)
To run the full open-source PaddleOCR engine and PostgreSQL database locally on your own hardware:
```bash
git clone https://github.com/harshpandey2207/true_label.git
cd true_label/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
