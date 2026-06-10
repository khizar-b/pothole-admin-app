"""
Impact Score Calculation Reference

This file explains how impact scores are calculated for each pothole.
"""

# FORMULA
# -------
# impact_score = (area_normalized * 0.6) + (confidence_score * 0.4)


# STEP 1: Normalize the Area
# ==========================
# - Bounding box area = bbox_width × bbox_height
# - Maximum image area = 640 × 480 = 307,200 pixels
# - Normalized area = (bbox_area / 307,200) × 100
# - Result: 0-100 scale

# Example:
#   bbox_width = 45, bbox_height = 50
#   bbox_area = 45 × 50 = 2,250
#   normalized = (2,250 / 307,200) × 100 = 0.73%


# STEP 2: Normalize Confidence Score
# ===================================
# - Confidence from CSV: 0.0 to 1.0
# - Convert to percentage: confidence × 100
# - Result: 0-100 scale

# Example:
#   confidence = 0.95
#   normalized = 0.95 × 100 = 95


# STEP 3: Calculate Impact Score
# ===============================
# impact_score = (area_normalized × 0.6) + (confidence_normalized × 0.4)

# Example with 60% weight on area, 40% weight on confidence:
#   area_normalized = 0.73
#   confidence = 95
#   impact_score = (0.73 × 0.6) + (95 × 0.4)
#                = 0.438 + 38
#                = 38.438


# STEP 4: Determine Impact Levels
# ================================

# Score: 0-30
#   Description: Minor pothole, low infrastructure impact
#   Bike Impact: LOW ✓ Bikeable with caution
#   Car Impact: LOW ✓ Minimal impact

# Score: 31-60
#   Description: Moderate pothole, moderate impact
#   Bike Impact: MEDIUM ⚠ Risk for cyclists
#   Car Impact: MEDIUM ⚠ Can cause discomfort

# Score: 61-100
#   Description: Severe pothole, high infrastructure impact
#   Bike Impact: HIGH ✗ Dangerous for cyclists
#   Car Impact: HIGH ✗ Risk of vehicle damage


# INTERPRETATION GUIDE
# ====================

# High Area + High Confidence = HIGHEST PRIORITY
#   Large pothole (60%+ of image) that's definitely detected
#   Impact Score: 70-100
#   Action: Urgent repair needed

# High Area + Medium Confidence = HIGH PRIORITY  
#   Large damage visible but detection confidence moderate
#   Impact Score: 50-70
#   Action: Schedule soon

# Medium Area + High Confidence = MEDIUM PRIORITY
#   Well-confirmed damage but not very large
#   Impact Score: 40-60
#   Action: Monitor and plan

# Low Area + Any Confidence = LOW PRIORITY
#   Small damage that might be minor pothole
#   Impact Score: 0-30
#   Action: Monitor for changes


# EXAMPLE CALCULATIONS
# ====================

# Pothole A:
#   bbox_width: 80px, bbox_height: 90px
#   confidence: 0.92
#   
#   area_norm = (7,200 / 307,200) × 100 = 2.34%
#   conf_norm = 0.92 × 100 = 92
#   impact = (2.34 × 0.6) + (92 × 0.4) = 1.40 + 36.8 = 38.2
#   Level: MEDIUM (31-60)


# Pothole B:
#   bbox_width: 30px, bbox_height: 35px
#   confidence: 0.78
#
#   area_norm = (1,050 / 307,200) × 100 = 0.34%
#   conf_norm = 0.78 × 100 = 78
#   impact = (0.34 × 0.6) + (78 × 0.4) = 0.20 + 31.2 = 31.4
#   Level: MEDIUM (31-60)


# Pothole C:
#   bbox_width: 120px, bbox_height: 150px
#   confidence: 0.95
#
#   area_norm = (18,000 / 307,200) × 100 = 5.86%
#   conf_norm = 0.95 × 100 = 95
#   impact = (5.86 × 0.6) + (95 × 0.4) = 3.52 + 38 = 41.52
#   Level: MEDIUM (31-60)


# Pothole D:
#   bbox_width: 250px, bbox_height: 280px
#   confidence: 0.88
#
#   area_norm = (70,000 / 307,200) × 100 = 22.79%
#   conf_norm = 0.88 × 100 = 88
#   impact = (22.79 × 0.6) + (88 × 0.4) = 13.67 + 35.2 = 48.87
#   Level: MEDIUM (31-60)


# DECISION MATRIX
# ===============

# For Road Maintenance Teams:
#
# HIGH Impact (61-100)
#   └─ Both bikes and cars: HIGH RISK
#   └─ Action: URGENT REPAIR - Schedule within 1 week
#   └─ Methods: Full patch repair or resurfacing
#
# MEDIUM Impact (31-60)
#   └─ Bikes: MEDIUM, Cars: MEDIUM
#   └─ Action: PLANNED REPAIR - Schedule within 2-4 weeks
#   └─ Methods: Temporary patch or permanent repair
#
# LOW Impact (0-30)
#   └─ Both bikes and cars: LOW RISK
#   └─ Action: MONITOR - Review periodically
#   └─ Methods: Watch for growth, schedule routine maintenance


# CSV FORMAT (INPUT)
# ==================
# Required columns for upload:
# image_name, timestamp, bbox_x, bbox_y, bbox_width, bbox_height, 
# confidence_score, latitude, longitude
#
# NOTE: Do NOT include impact_score in input CSV - it's calculated automatically!


# DATABASE STORAGE
# ================
# The system stores:
# - impact_score (Float): Calculated score 0-100
# - bike_impact (String): 'low', 'medium', or 'high'
# - car_impact (String): 'low', 'medium', or 'high'
#
# These are created automatically when CSV is uploaded
