"""
Database migration script to add impact score columns
"""
from app import create_app
from models import db
from sqlalchemy import text

def migrate_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='pothole_records' AND column_name='impact_score'
            """))
            
            if result.fetchone():
                print("Columns already exist. No migration needed.")
                return
            
            print("Adding new columns to pothole_records table...")
            
            # Add impact_score column
            db.session.execute(text("""
                ALTER TABLE pothole_records 
                ADD COLUMN impact_score FLOAT DEFAULT 0.0 NOT NULL
            """))
            
            # Add bike_impact column
            db.session.execute(text("""
                ALTER TABLE pothole_records 
                ADD COLUMN bike_impact VARCHAR(20) DEFAULT 'low' NOT NULL
            """))
            
            # Add car_impact column
            db.session.execute(text("""
                ALTER TABLE pothole_records 
                ADD COLUMN car_impact VARCHAR(20) DEFAULT 'low' NOT NULL
            """))
            
            # Remove damage_type column if it exists
            db.session.execute(text("""
                ALTER TABLE pothole_records 
                DROP COLUMN IF EXISTS damage_type
            """))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            print("Added columns: impact_score, bike_impact, car_impact")
            print("Removed column: damage_type")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate_database()
