# True Label: Legal Metrology AI Engine

True Label is an advanced legal metrology and AI-powered product label compliance scanner. It uses computer vision and AR to verify packaged commodities against Legal Metrology Rules (MRP, Manufacturing Date, Net Quantity, Manufacturer details, etc.).

> **Architecture Notice (Live Demo)**
> The core open-source architecture of True Label utilizes PaddleOCR (PP-OCRv4) to handle complex metrology extraction and AR bounding boxes. Due to the high compute constraints (0.1 vCPU limits) of our free-tier hosting which cause 2-5 minute processing delays, this live web demo temporarily routes inference through a lightweight cloud API to ensure fast evaluation for the judges. You can view our full open-source PaddleOCR fallback implementation in `backend/app/services/ai_engine/metrology_engine.py`.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Learn Flutter](https://docs.flutter.dev/get-started/learn-flutter)
- [Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Flutter learning resources](https://docs.flutter.dev/reference/learning-resources)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
