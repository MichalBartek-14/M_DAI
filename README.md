# 🛰️ Sentinel-2 Vegetation Dashboard

AI - author collaboration project to deploy a dashboard using S2 satellite imagery.
A dashboard for visualizing and analyzing Sentinel-2 vegetation indices (NDVI, NDWI, EVI, SAVI, NDMI) over any user-defined area of interest.

[![Deploy Frontend](https://img.shields.io/badge/Deploy-Vercel-black)](https://vercel.com)
[![Deploy Backend](https://img.shields.io/badge/Deploy-Render-purple)](https://render.com)
[![API Docs](https://img.shields.io/badge/API-FastAPI-009688)](http://localhost:8000/api/docs)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗺️ **Interactive Map** | Draw polygons/rectangles or enter coordinates |
| 📊 **5 Spectral Indices** | NDVI, NDWI, EVI, SAVI, NDMI with colour scales |
| 📈 **Time-series** | 16-day composite charts for any date range |
| ☁️ **Cloud Masking** | Automatic SCL-based cloud/shadow filtering |
| 🎯 **Area Statistics** | Mean, median, std, histogram per AOI |
| ⬇️ **Export** | Download as colourised PNG or float32 GeoTIFF |
| 🌾 **Use-case Presets** | Agriculture, Forestry, Water, Drought monitoring |
| 🔑 **Demo Mode** | Works without API keys using synthetic data |

---

## 🏗️ Architecture

```
sentinel-dashboard/
├── backend/                    # Python FastAPI service
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py       # Settings (pydantic-settings)
│   │   │   ├── schemas.py      # Pydantic models
│   │   │   ├── auth.py         # Sentinel Hub OAuth2
│   │   │   └── cache.py        # In-memory + disk tile cache
│   │   ├── api/
│   │   │   ├── indices.py      # POST /api/indices/compute
│   │   │   ├── tiles.py        # GET  /api/tiles/{index}/{z}/{x}/{y}.png
│   │   │   ├── timeseries.py   # POST /api/timeseries/
│   │   │   ├── stats.py        # POST /api/stats/area
│   │   │   └── export.py       # POST /api/export/{png,geotiff}
│   │   └── services/
│   │       ├── sentinel.py     # Sentinel Hub Process API wrapper
│   │       ├── indices.py      # NDVI/NDWI/EVI/SAVI/NDMI formulas
│   │       ├── timeseries.py   # Time-series computation
│   │       └── colormap.py     # Float array → PNG renderer
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
└── frontend/                   # React + Vite application
    ├── src/
    │   ├── App.jsx             # Root layout
    │   ├── store/
    │   │   └── useStore.js     # Zustand global state
    │   ├── services/
    │   │   └── api.js          # Axios API client
    │   ├── utils/
    │   │   ├── indexMeta.js    # Index metadata + presets
    │   │   └── mapUtils.js     # Coordinate helpers
    │   ├── components/
    │   │   ├── Map/            # Leaflet map + draw tools
    │   │   ├── Charts/         # Recharts time-series panel
    │   │   ├── Controls/       # Sidebar controls
    │   │   └── UI/             # TopBar, Legend, StatsPanel
    │   └── styles/
    │       └── global.css      # Design system variables
    ├── package.json
    ├── vite.config.js
    └── .env.example
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- Optional: Sentinel Hub account (free tier available)

---

### 1. Clone the repository

```bash
git clone https://github.com/your-org/sentinel-dashboard.git
cd sentinel-dashboard
```

---

### 2. Backend setup

```bash
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Sentinel Hub credentials (see API Keys section below)

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/api/docs`

> **No API keys?** The backend runs in **demo mode** automatically — it generates realistic synthetic imagery so you can explore the UI fully.

---

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Set VITE_API_URL=http://localhost:8000 (default, no change needed for local dev)

# Start the dev server
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 🔑 API Key Configuration

### Option A — Sentinel Hub (Recommended)

Sentinel Hub provides the highest-quality Sentinel-2 processing via its Process API.

1. **Register** at [https://www.sentinel-hub.com/](https://www.sentinel-hub.com/) (free trial available)
2. Go to **Dashboard → User Settings → OAuth clients**
3. Click **"+ Add"** to create a new OAuth client
4. Copy the **Client ID** and **Client Secret**
5. Add to `backend/.env`:

```env
SENTINELHUB_CLIENT_ID=your-client-id
SENTINELHUB_CLIENT_SECRET=your-client-secret
```

**Free tier limits:** 30,000 processing units/month (~300 full-res tile requests)

---

### Option B — Copernicus Dataspace (Free, No Account Needed for STAC)

The STAC scene search endpoint is publicly accessible:

```
https://catalogue.dataspace.copernicus.eu/stac/search
```

For imagery download (Process API), register at [https://dataspace.copernicus.eu/](https://dataspace.copernicus.eu/) — it's free.

```env
# After registration, use Dataspace credentials:
SENTINELHUB_CLIENT_ID=your-cdse-client-id
SENTINELHUB_CLIENT_SECRET=your-cdse-client-secret
```

---

### Option C — Google Earth Engine (Advanced)

For very large areas or complex analysis, enable the GEE backend:

1. Create a GCP project and enable the Earth Engine API
2. Create a service account and download the JSON key file
3. Register the service account at [https://code.earthengine.google.com/register](https://code.earthengine.google.com/register)
4. Add to `backend/.env`:

```env
USE_GEE=true
GEE_SERVICE_ACCOUNT=my-account@my-project.iam.gserviceaccount.com
GEE_KEY_FILE=/path/to/service-account-key.json
```

Then uncomment `earthengine-api` in `requirements.txt` and reinstall.

---

## 📦 Deployment

### Frontend → Vercel

```bash
cd frontend

# Build
npm run build

# Deploy with Vercel CLI
npx vercel --prod
```

Or connect your GitHub repo to [vercel.com](https://vercel.com) for automatic deployments.

**Environment variables to set in Vercel dashboard:**
```
VITE_API_URL=https://your-backend.onrender.com
```

---

### Backend → Render

1. Push the `backend/` folder to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your repo and configure:

| Setting | Value |
|---|---|
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Environment** | Python 3.11 |

4. Add environment variables:
   - `SENTINELHUB_CLIENT_ID`
   - `SENTINELHUB_CLIENT_SECRET`
   - `ALLOWED_ORIGINS` → `["https://your-app.vercel.app"]`

---

### Backend → Fly.io

```bash
cd backend

# Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
fly launch --name sentinel-dashboard-api

# Set secrets
fly secrets set SENTINELHUB_CLIENT_ID=xxx SENTINELHUB_CLIENT_SECRET=yyy

# Deploy
fly deploy
```

---

### Docker (Self-hosted)

```bash
# Build and run backend
cd backend
docker build -t sentinel-backend .
docker run -p 8000:8000 \
  -e SENTINELHUB_CLIENT_ID=xxx \
  -e SENTINELHUB_CLIENT_SECRET=yyy \
  sentinel-backend

# Serve frontend (after build)
cd frontend
npm run build
npx serve dist -p 3000
```

---

## 🗺️ API Reference

### `POST /api/indices/compute`
Compute index metadata and get tile URL.

```json
{
  "aoi": {
    "bbox": { "min_lon": 4.72, "min_lat": 52.27, "max_lon": 5.08, "max_lat": 52.47 }
  },
  "start_date": "2024-04-01",
  "end_date": "2024-09-30",
  "index": "NDVI",
  "cloud_cover_max": 30,
  "resolution": 10
}
```

### `GET /api/tiles/{index}/{z}/{x}/{y}.png`
XYZ tile endpoint. Query params: `start`, `end`, `bbox`, `cloud`, `res`.

### `POST /api/timeseries/`
Get 16-day mean index values over time.

```json
{
  "aoi": { "bbox": { ... } },
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "indices": ["NDVI", "EVI"],
  "cloud_cover_max": 30
}
```

### `POST /api/stats/area`
Compute area statistics (mean, median, std, histogram).

### `POST /api/export/png` / `POST /api/export/geotiff`
Download raster as colourised PNG or float32 GeoTIFF.

---

## 🧮 Spectral Index Formulas

| Index | Formula | Bands | Best for |
|---|---|---|---|
| **NDVI** | (NIR−Red)/(NIR+Red) | B08, B04 | Vegetation density |
| **NDWI** | (Green−NIR)/(Green+NIR) | B03, B08 | Water bodies |
| **EVI** | 2.5×(NIR−Red)/(NIR+6×Red−7.5×Blue+1) | B08, B04, B02 | Dense canopy |
| **SAVI** | (NIR−Red)/(NIR+Red+0.5)×1.5 | B08, B04 | Arid vegetation |
| **NDMI** | (NIR−SWIR1)/(NIR+SWIR1) | B8A, B11 | Moisture/drought |

---

## ⚡ Performance Notes

- **Tile caching:** Rendered tiles are cached to disk for 24 h at `/tmp/sentinel_tile_cache`
- **Resolution:** Time-series uses 60 m resolution for speed; export uses 10 m
- **AOI limit:** Default maximum AOI area is 5,000 km² (configurable via `MAX_AOI_AREA_KM2`)
- **Demo mode:** When no API credentials are set, synthetic data is returned in <100 ms

---

## 🛠️ Development Tips

```bash
# Run backend tests
cd backend
pytest tests/ -v

# Check API health
curl http://localhost:8000/api/health

# Inspect tile cache
ls /tmp/sentinel_tile_cache/

# Clear tile cache
rm -rf /tmp/sentinel_tile_cache/*
```

---

## 📄 License

MIT — free to use, modify, and deploy.
