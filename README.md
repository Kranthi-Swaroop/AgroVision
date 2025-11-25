# 🌱 AgroSentinel

**AI-Powered Crop Disease Detection System for Indian Farmers**

An intelligent mobile-first web app that helps farmers detect crop diseases, get treatment recommendations, and manage field health using AI, weather data, and an integrated chatbot.

## ✨ Features

- 🔬 **AI Disease Detection** - EfficientNet-B3 model with 99.84% accuracy on 15 crop diseases
- 🌤️ **Weather-Correlated Risk** - Real-time weather integration for disease risk assessment
- 💊 **ICAR Treatment Database** - Authentic medication recommendations from Indian agricultural research
- 🗺️ **Field Map** - Drone view simulation with satellite imagery and disease clustering
- 🤖 **AI Chat Assistant** - Gemini 2.0 powered farming assistant
- 🌐 **Multi-Language** - English, Hindi, Telugu, Tamil, Kannada
- 📱 **PWA Offline Mode** - Works without internet, syncs when connected
- 🌙 **Dark/Light Theme** - Eye-friendly interface

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, ONNX Runtime, Motor (MongoDB), Google Gemini AI |
| **Frontend** | React 18, Vite 5, Tailwind CSS, Leaflet Maps, Framer Motion |
| **Database** | MongoDB |
| **ML Model** | EfficientNet-B3 (ONNX format, 43.8 MB) |
| **APIs** | OpenWeatherMap, Google Gemini 2.0 |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file:
```env
MONGODB_URI=mongodb://localhost:27017/agrosentinel
OPENWEATHERMAP_API_KEY=your_openweathermap_key
GEMINI_API_KEY=your_gemini_api_key
```

Run backend:
```bash
uvicorn app.main:app --port 8001
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## ☁️ Deploy to Railway (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub"
   - Select your `AgroVision` repository
   - Add environment variables:
     - `MONGODB_URI` - Get free MongoDB Atlas: [mongodb.com/atlas](https://mongodb.com/atlas)
     - `OPENWEATHERMAP_API_KEY` - Get free: [openweathermap.org/api](https://openweathermap.org/api)
     - `GEMINI_API_KEY` - Get free: [makersuite.google.com](https://makersuite.google.com/app/apikey)
   - Railway will auto-detect and deploy!

3. **Add MongoDB** (if using Railway's built-in)
   - Click "New" → "Database" → "MongoDB"
   - Copy the connection string to `MONGODB_URI`

## 📱 Supported Crops & Diseases

| Crop | Diseases Detected |
|------|-------------------|
| 🍅 Tomato | Late Blight, Early Blight, Bacterial Spot, Leaf Mold, Mosaic Virus, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Healthy |
| 🥔 Potato | Late Blight, Early Blight, Healthy |
| 🌶️ Pepper | Bacterial Spot, Healthy |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Full disease analysis with weather & risk |
| POST | `/api/predict` | Quick disease prediction |
| POST | `/api/chat` | Chat with AI assistant |
| GET | `/api/weather` | Get weather data |
| GET | `/api/remedies/{disease}` | Get treatment info |
| GET | `/api/history/location` | Location-based scan history |

## 📂 Project Structure

```
AgroVision/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Environment config
│   │   ├── routes/          # API routes
│   │   └── services/        # Business logic
│   ├── models/              # ONNX model files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # UI components
│   │   ├── i18n/           # Translations
│   │   └── services/       # API client
│   └── package.json
└── training/                # Model training scripts
```

## 🎯 Model Performance

| Metric | Value |
|--------|-------|
| Validation Accuracy | 99.84% |
| Model Architecture | EfficientNet-B3 |
| Parameters | 11.49M |
| ONNX Size | 43.8 MB |
| Inference Time | ~100ms |

## 📄 License

MIT License - Feel free to use for your hackathon or project!

## 🙏 Acknowledgments

- PlantVillage Dataset
- ICAR (Indian Council of Agricultural Research)
- OpenWeatherMap API
- Google Gemini AI
