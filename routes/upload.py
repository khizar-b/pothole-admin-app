from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, PotholeRecord
from utils import normalize_area, calculate_impact_score, get_impact_level
import pandas as pd
import os
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload-csv', methods=['POST'])
@jwt_required()
def upload_csv():
    try:
        current_user = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in request'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Read CSV file
        df = pd.read_csv(file)
        
        # Validate required columns (removed damage_type)
        required_columns = [
            'image_name', 'timestamp', 'bbox_x', 'bbox_y', 
            'bbox_width', 'bbox_height', 'confidence_score', 
            'latitude', 'longitude'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        # Process and insert records with impact score calculation
        records_added = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Parse timestamp
                timestamp = pd.to_datetime(row['timestamp'])
                
                # Calculate area and impact score
                bbox_width = float(row['bbox_width'])
                bbox_height = float(row['bbox_height'])
                confidence_score = float(row['confidence_score'])
                
                area_normalized = normalize_area(bbox_width, bbox_height)
                impact_score = calculate_impact_score(area_normalized, confidence_score)
                impact_levels = get_impact_level(impact_score)
                
                # Create record
                record = PotholeRecord(
                    image_name=str(row['image_name']),
                    timestamp=timestamp,
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
                    uploaded_by=current_user
                )
                
                db.session.add(record)
                records_added += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Commit all records
        db.session.commit()
        
        response = {
            'message': 'CSV processed successfully',
            'records_added': records_added,
            'total_rows': len(df)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/potholes', methods=['GET'])
@jwt_required()
def get_potholes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Query with pagination
        pagination = PotholeRecord.query.order_by(
            PotholeRecord.uploaded_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        records = [record.to_dict() for record in pagination.items]
        
        return jsonify({
            'records': records,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/potholes/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_pothole(record_id):
    try:
        record = PotholeRecord.query.get(record_id)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': 'Record deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        total_records = PotholeRecord.query.count()
        
        # Calculate average confidence score
        avg_confidence = db.session.query(
            db.func.avg(PotholeRecord.confidence_score)
        ).scalar() or 0
        
        # Get impact score distribution
        high_impact = PotholeRecord.query.filter(PotholeRecord.impact_score > 60).count()
        medium_impact = PotholeRecord.query.filter(
            db.and_(PotholeRecord.impact_score > 30, PotholeRecord.impact_score <= 60)
        ).count()
        low_impact = PotholeRecord.query.filter(PotholeRecord.impact_score <= 30).count()
        
        # Bike impact distribution
        bike_high = PotholeRecord.query.filter(PotholeRecord.bike_impact == 'high').count()
        bike_medium = PotholeRecord.query.filter(PotholeRecord.bike_impact == 'medium').count()
        bike_low = PotholeRecord.query.filter(PotholeRecord.bike_impact == 'low').count()
        
        # Car impact distribution
        car_high = PotholeRecord.query.filter(PotholeRecord.car_impact == 'high').count()
        car_medium = PotholeRecord.query.filter(PotholeRecord.car_impact == 'medium').count()
        car_low = PotholeRecord.query.filter(PotholeRecord.car_impact == 'low').count()
        
        # Get highest impact potholes
        top_potholes = PotholeRecord.query.order_by(
            PotholeRecord.impact_score.desc()
        ).limit(5).all()
        
        top_potholes_data = [{
            'id': p.id,
            'image_name': p.image_name,
            'impact_score': p.impact_score,
            'bike_impact': p.bike_impact,
            'car_impact': p.car_impact,
            'confidence_score': p.confidence_score,
            'latitude': p.latitude,
            'longitude': p.longitude
        } for p in top_potholes]
        
        return jsonify({
            'total_records': total_records,
            'average_confidence_score': round(avg_confidence * 100, 2),
            'impact_score_distribution': {
                'high': high_impact,
                'medium': medium_impact,
                'low': low_impact
            },
            'bike_impact_distribution': {
                'high': bike_high,
                'medium': bike_medium,
                'low': bike_low
            },
            'car_impact_distribution': {
                'high': car_high,
                'medium': car_medium,
                'low': car_low
            },
            'top_impact_potholes': top_potholes_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@upload_bp.route('/export-csv', methods=['GET'])
@jwt_required()
def export_csv():
    try:
        # Get all records from database
        records = PotholeRecord.query.all()
        
        if not records:
            return jsonify({'error': 'No records to export'}), 404
        
        # Create DataFrame from records
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'image_name': record.image_name,
                'timestamp': record.timestamp.isoformat(),
                'bbox_x': record.bbox_x,
                'bbox_y': record.bbox_y,
                'bbox_width': record.bbox_width,
                'bbox_height': record.bbox_height,
                'confidence_score': record.confidence_score,
                'impact_score': record.impact_score,
                'bike_impact': record.bike_impact,
                'car_impact': record.car_impact,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'uploaded_at': record.uploaded_at.isoformat(),
                'uploaded_by': record.uploaded_by
            })
        
        df = pd.DataFrame(data)
        
        # Return CSV data
        csv_data = df.to_csv(index=False)
        
        return {
            'csv_data': csv_data,
            'filename': f'pothole_records_with_impact_scores_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }, 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/delete-duplicates', methods=['POST'])
@jwt_required()
def delete_duplicates():
    try:
        # Get all records grouped by image_name
        from sqlalchemy import func
        
        # Find duplicate image names
        duplicates = db.session.query(
            PotholeRecord.image_name,
            func.count(PotholeRecord.id).label('count'),
            func.min(PotholeRecord.id).label('keep_id')
        ).group_by(PotholeRecord.image_name).having(func.count(PotholeRecord.id) > 1).all()
        
        if not duplicates:
            return jsonify({
                'message': 'No duplicate records found',
                'deleted_count': 0
            }), 200
        
        deleted_count = 0
        
        # For each set of duplicates, keep the first (lowest ID) and delete the rest
        for dup in duplicates:
            image_name = dup.image_name
            keep_id = dup.keep_id
            
            # Delete all records with this image_name except the one with keep_id
            deleted = PotholeRecord.query.filter(
                PotholeRecord.image_name == image_name,
                PotholeRecord.id != keep_id
            ).delete()
            
            deleted_count += deleted
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {deleted_count} duplicate records',
            'deleted_count': deleted_count,
            'duplicate_groups': len(duplicates)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
