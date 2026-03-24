"""
Integration tests for the FastAPI endpoints.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_index_meta_all():
    resp = client.get("/api/indices/meta")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) >= {"NDVI", "NDWI", "EVI", "SAVI", "NDMI"}


def test_index_meta_single():
    resp = client.get("/api/indices/meta/NDVI")
    assert resp.status_code == 200
    data = resp.json()
    assert data["label"] == "Normalized Difference Vegetation Index"


def test_index_meta_unknown():
    resp = client.get("/api/indices/meta/FAKE")
    assert resp.status_code == 404


SAMPLE_REQUEST = {
    "aoi": {
        "bbox": {
            "min_lon": 4.72,
            "min_lat": 52.27,
            "max_lon": 5.08,
            "max_lat": 52.47,
        }
    },
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "index": "NDVI",
    "cloud_cover_max": 30,
    "resolution": 10,
}


def test_compute_index():
    resp = client.post("/api/indices/compute", json=SAMPLE_REQUEST)
    assert resp.status_code == 200
    data = resp.json()
    assert data["index"] == "NDVI"
    assert "tile_url" in data
    assert "stats" in data
    assert "scenes" in data


def test_timeseries():
    payload = {
        "aoi": SAMPLE_REQUEST["aoi"],
        "start_date": "2024-01-01",
        "end_date": "2024-04-30",
        "indices": ["NDVI", "EVI"],
        "cloud_cover_max": 30,
    }
    resp = client.post("/api/timeseries/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "NDVI" in data
    assert "EVI" in data
    assert len(data["NDVI"]["data"]) > 0


def test_tile_endpoint():
    resp = client.get(
        "/api/tiles/NDVI/5/16/10.png",
        params={
            "start": "2024-01-01",
            "end":   "2024-06-30",
            "bbox":  "4.72,52.27,5.08,52.47",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert resp.content[:4] == b"\x89PNG"


def test_invalid_bbox():
    payload = {
        "aoi": {
            "bbox": {
                "min_lon": 10.0,
                "min_lat": 52.0,
                "max_lon": 5.0,   # max < min — should fail
                "max_lat": 54.0,
            }
        },
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "index": "NDVI",
    }
    resp = client.post("/api/indices/compute", json=payload)
    assert resp.status_code == 422  # Validation error
