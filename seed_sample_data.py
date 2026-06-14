"""Seed pothole_records from a sample CSV using the same impact-score
logic as the /api/upload-csv endpoint."""
import sys

import pandas as pd

from app import create_app
from models import db, PotholeRecord
from utils import normalize_area, calculate_impact_score, get_impact_level


def seed(csv_path):
    app = create_app()
    with app.app_context():
        df = pd.read_csv(csv_path)
        added = 0
        for _, row in df.iterrows():
            if PotholeRecord.query.filter_by(image_name=str(row['image_name'])).first():
                continue
            bbox_width = float(row['bbox_width'])
            bbox_height = float(row['bbox_height'])
            confidence_score = float(row['confidence_score'])

            area_normalized = normalize_area(bbox_width, bbox_height)
            impact_score = calculate_impact_score(area_normalized, confidence_score)
            impact_levels = get_impact_level(impact_score)

            db.session.add(PotholeRecord(
                image_name=str(row['image_name']),
                timestamp=pd.to_datetime(row['timestamp']),
                bbox_x=float(row['bbox_x']),
                bbox_y=float(row['bbox_y']),
                bbox_width=bbox_width,
                bbox_height=bbox_height,
                confidence_score=confidence_score,
                impact_score=impact_score,
                bike_impact=impact_levels['bike_impact'],
                car_impact=impact_levels['car_impact'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                uploaded_by='seed-script',
            ))
            added += 1
        db.session.commit()
        print(f"Seeded {added} records from {csv_path} "
              f"(total in db: {PotholeRecord.query.count()})")


if __name__ == '__main__':
    seed(sys.argv[1] if len(sys.argv) > 1 else 'sample_data_updated.csv')
