"""
Utility functions for pothole analysis
"""

def normalize_area(bbox_width, bbox_height):
    """
    Normalize the bounding box area to a 0-100 scale.
    Assumes a typical image size of 640x480 pixels
    """
    max_area = 640 * 480  # Maximum possible area
    area = bbox_width * bbox_height
    normalized_area = (area / max_area) * 100
    return min(normalized_area, 100)  # Cap at 100


def calculate_impact_score(area_normalized, confidence_score):
    """
    Calculate impact score using the formula:
    impact_score = (area_normalized * 0.6) + (confidence * 0.40)
    
    Args:
        area_normalized: Normalized area (0-100)
        confidence_score: Confidence score (0-1)
    
    Returns:
        impact_score: Float between 0-100
    """
    # Convert confidence from 0-1 to 0-100 scale
    confidence_normalized = confidence_score * 100
    
    impact_score = (area_normalized * 0.6) + (confidence_normalized * 0.40)
    return min(impact_score, 100)  # Cap at 100


def get_impact_level(impact_score):
    """
    Get bike and car impact levels based on impact score.
    
    Score ranges:
    - 0-30: car=low, bike=medium
    - 31-60: car=medium, bike=high
    - 61-100: car=high, bike=high
    
    Args:
        impact_score: Impact score (0-100)
    
    Returns:
        dict: {'bike_impact': str, 'car_impact': str}
    """
    if impact_score <= 30:
        return {
            'bike_impact': 'medium',
            'car_impact': 'low'
        }
    elif impact_score <= 60:
        return {
            'bike_impact': 'high',
            'car_impact': 'medium'
        }
    else:  # 61-100
        return {
            'bike_impact': 'high',
            'car_impact': 'high'
        }
