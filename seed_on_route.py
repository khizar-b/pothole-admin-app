"""Seed demo potholes exactly onto a real Routes API polyline so the mobile
app shows potholes sitting on the computed route. Usage:

    python seed_on_route.py <origin_lat> <origin_lng> <dest_lat> <dest_lng> <api_key>
"""
import json
import sys
import urllib.request
from datetime import datetime

from app import create_app
from models import db, PotholeRecord
from utils import normalize_area, calculate_impact_score, get_impact_level


def get_polyline(o_lat, o_lng, d_lat, d_lng, key):
    body = json.dumps({
        "origin": {"location": {"latLng": {"latitude": o_lat, "longitude": o_lng}}},
        "destination": {"location": {"latLng": {"latitude": d_lat, "longitude": d_lng}}},
        "travelMode": "DRIVE",
        "computeAlternativeRoutes": False,
    }).encode()
    req = urllib.request.Request(
        "https://routes.googleapis.com/directions/v2:computeRoutes",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": "routes.polyline.encodedPolyline",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    return data["routes"][0]["polyline"]["encodedPolyline"]


def decode_polyline(encoded):
    points, index, lat, lng = [], 0, 0, 0
    while index < len(encoded):
        for is_lat in (True, False):
            shift, result = 0, 0
            while True:
                byte = ord(encoded[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else result >> 1
            if is_lat:
                lat += delta
            else:
                lng += delta
        points.append((lat / 1e5, lng / 1e5))
    return points


def seed(o_lat, o_lng, d_lat, d_lng, key):
    pts = decode_polyline(get_polyline(o_lat, o_lng, d_lat, d_lng, key))
    print(f"Route has {len(pts)} points; seeding potholes on the final approach.")

    # Pick points near the destination end of the route (shared by all routes
    # to this destination) plus a couple mid-route, with varied severities.
    n = len(pts)
    picks = [
        (pts[int(n * 0.55)], 30, 35, 0.82),   # smaller -> low/medium
        (pts[int(n * 0.75)], 60, 70, 0.92),   # large -> high
        (pts[int(n * 0.88)], 45, 50, 0.88),   # medium
        (pts[int(n * 0.95)], 80, 90, 0.95),   # very large -> high
    ]

    app = create_app()
    with app.app_context():
        # Clear previous demo-on-route rows so reruns stay clean.
        PotholeRecord.query.filter(
            PotholeRecord.image_name.like('route_demo_%')).delete(
            synchronize_session=False)
        for i, ((lat, lng), w, h, conf) in enumerate(picks, 1):
            area = normalize_area(w, h)
            score = calculate_impact_score(area, conf)
            levels = get_impact_level(score)
            db.session.add(PotholeRecord(
                image_name=f'route_demo_{i:02d}.jpg',
                timestamp=datetime(2026, 6, 14, 9, i),
                bbox_x=150, bbox_y=180, bbox_width=w, bbox_height=h,
                confidence_score=conf, impact_score=score,
                bike_impact=levels['bike_impact'], car_impact=levels['car_impact'],
                latitude=lat, longitude=lng, uploaded_by='route-demo'))
            print(f"  #{i}: ({lat:.5f},{lng:.5f}) score={score:.1f} "
                  f"car={levels['car_impact']} bike={levels['bike_impact']}")
        db.session.commit()
        print(f"Done. Total potholes in db: {PotholeRecord.query.count()}")


if __name__ == '__main__':
    seed(float(sys.argv[1]), float(sys.argv[2]),
         float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
