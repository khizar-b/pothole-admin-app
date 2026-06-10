"""
Script to recalculate impact scores for existing records with the corrected logic:
- car=low → bike=medium
- car=medium → bike=high
- car=high → bike=high
"""
from app import create_app
from models import db, PotholeRecord
from utils import normalize_area, calculate_impact_score, get_impact_level

def fix_impact_scores():
    app = create_app()
    
    with app.app_context():
        # Get all records
        records = PotholeRecord.query.all()
        
        if not records:
            print("No records found.")
            return
        
        print(f"Found {len(records)} records to update...")
        updated_count = 0
        
        for record in records:
            # Recalculate impact score
            area_normalized = normalize_area(record.bbox_width, record.bbox_height)
            impact_score = calculate_impact_score(area_normalized, record.confidence_score)
            impact_levels = get_impact_level(impact_score)
            
            # Update the record
            record.impact_score = impact_score
            record.bike_impact = impact_levels['bike_impact']
            record.car_impact = impact_levels['car_impact']
            
            updated_count += 1
            
            if updated_count % 100 == 0:
                print(f"Updated {updated_count} records...")
        
        # Commit all changes
        db.session.commit()
        print(f"✅ Successfully updated {updated_count} records with corrected impact logic!")
        
        # Show some examples
        print("\n📊 Sample updated records:")
        samples = PotholeRecord.query.limit(5).all()
        for record in samples:
            print(f"  ID {record.id}: Impact Score={record.impact_score:.1f}, "
                  f"Bike={record.bike_impact}, Car={record.car_impact}")

if __name__ == '__main__':
    fix_impact_scores()
