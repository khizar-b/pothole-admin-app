"""Public read-only endpoints consumed by the mobile app (no admin JWT)."""
from flask import Blueprint, request, jsonify
from models import PotholeRecord

mobile_bp = Blueprint('mobile', __name__)


@mobile_bp.route('/public/potholes', methods=['GET'])
def public_potholes():
    """Return potholes, optionally filtered to a bounding box.

    Query params (all optional, pass all four to filter):
      min_lat, max_lat, min_lng, max_lng
    """
    try:
        query = PotholeRecord.query

        bounds = {p: request.args.get(p, type=float)
                  for p in ('min_lat', 'max_lat', 'min_lng', 'max_lng')}
        if all(v is not None for v in bounds.values()):
            query = query.filter(
                PotholeRecord.latitude >= bounds['min_lat'],
                PotholeRecord.latitude <= bounds['max_lat'],
                PotholeRecord.longitude >= bounds['min_lng'],
                PotholeRecord.longitude <= bounds['max_lng'],
            )

        records = query.all()
        return jsonify({
            'potholes': [{
                'id': r.id,
                'latitude': r.latitude,
                'longitude': r.longitude,
                'impact_score': r.impact_score,
                'bike_impact': r.bike_impact,
                'car_impact': r.car_impact,
                'confidence_score': r.confidence_score,
            } for r in records],
            'total': len(records),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
