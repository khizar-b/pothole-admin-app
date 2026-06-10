# AdminVision Panel - Enhanced Features Guide

## Recent Updates

### 1. **Color Theme Update** ✅
- Entire UI redesigned with a professional grey/asphalt theme
- Matches road infrastructure aesthetic
- Updated all buttons, cards, and navigation elements

### 2. **Pothole Classification Removed** ✅
- Removed the `damage_type` field (previously had 3 types)
- Now focused on single "pothole" classification
- Streamlined CSV upload requirements

### 3. **Impact Score Calculator** ✅
The system now automatically calculates impact scores using:

```
impact_score = (area_normalized * 0.6) + (confidence_score * 0.4)
```

Where:
- **area_normalized**: Pothole area as percentage of image (0-100)
- **confidence_score**: Detection confidence (0-1), normalized to 0-100

**Impact Levels:**
- **0-30**: Bike Impact = Low, Car Impact = Low
- **31-60**: Bike Impact = Medium, Car Impact = Medium
- **61-100**: Bike Impact = High, Car Impact = High

### 4. **Enhanced Statistics Dashboard** ✅
The dashboard now displays:
- Total records count
- Average confidence score
- Impact score distribution (High/Medium/Low)
- Bike impact distribution
- Car impact distribution
- Top 5 highest impact potholes with detailed metrics

### 5. **CSV Export with Impact Scores** ✅
New feature to export all pothole records with calculated impact scores:
- Click "📥 Export with Impact Scores" button
- Downloads CSV file with all records
- Includes: ID, image name, timestamp, coordinates, scores, impact levels

### 6. **Admin Registration System** ✅
New registration page with:
- Username and password creation
- Email field (optional)
- Password confirmation
- Account validation
- Link to registration from login page

---

## Setting Up Google Sign-In (Optional)

To enable Google Sign-In functionality, follow these steps:

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown and select "New Project"
3. Enter project name: "AdminVision Panel"
4. Click "Create"

### Step 2: Create OAuth 2.0 Credentials

1. In the Google Cloud Console, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. If prompted, configure the OAuth consent screen first:
   - User Type: External
   - Fill in app name and user support email
   - Authorized domains: Add your domain (e.g., localhost, your-domain.com)
4. Application type: Web application
5. Name: "AdminVision Panel"

### Step 3: Configure Redirect URIs

Add these Authorized redirect URIs:
- `http://localhost:5000/api/auth/google-callback`
- `http://localhost:5000/register`
- `https://your-domain.com/api/auth/google-callback` (for production)

### Step 4: Copy Your Client ID

1. Copy the "Client ID" from your credentials
2. Update `register.html` at line ~56:
   ```javascript
   client_id: 'YOUR_CLIENT_ID_HERE'
   ```
   Replace `YOUR_CLIENT_ID_HERE` with your actual Google Client ID

### Step 5: Update Backend (Optional)

If you want to verify tokens server-side, install:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 6: Test the Integration

1. Navigate to http://localhost:5000/register
2. The "Sign up with Google" button should now be functional
3. Click it to authenticate with your Google account

---

## CSV Upload Format

Your CSV file should contain these columns (damage_type is NO LONGER required):

| Column | Type | Description |
|--------|------|-------------|
| image_name | String | Name of the pothole image |
| timestamp | DateTime | Date/time of detection (ISO format) |
| bbox_x | Float | X coordinate of bounding box |
| bbox_y | Float | Y coordinate of bounding box |
| bbox_width | Float | Width of bounding box |
| bbox_height | Float | Height of bounding box |
| confidence_score | Float | Detection confidence (0-1) |
| latitude | Float | GPS latitude |
| longitude | Float | GPS longitude |

**Impact scores are calculated automatically** - no need to include them in your CSV!

---

## Database Schema Changes

### PotholeRecord Model
New fields:
- `impact_score` (Float): Calculated impact score (0-100)
- `bike_impact` (String): Impact level for bikes (low/medium/high)
- `car_impact` (String): Impact level for cars (low/medium/high)

Removed fields:
- `damage_type` (no longer used)

---

## API Endpoints

### New Endpoints:

**POST /api/auth/register**
- Register a new admin account
- Body: `{username, password, email (optional)}`

**GET /api/export-csv**
- Export all pothole records with impact scores
- Returns: CSV file download

**GET /api/stats** (Enhanced)
- Returns detailed statistics including:
  - Average confidence score
  - Impact score distribution
  - Bike impact distribution
  - Car impact distribution
  - Top 5 highest impact potholes

---

## Technology Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt
- **Database**: SQLite (default)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: JWT (plus optional Google OAuth)

---

## Troubleshooting

### Database Errors
Run the init script to reset the database:
```bash
python init_db.py
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### CSV Upload Issues
- Verify all required columns are present
- Check data types (confidence_score should be 0-1, not 0-100)
- Ensure timestamps are in ISO format

### Google Sign-In Not Working
- Verify Client ID is correctly copied
- Check that registered domain/localhost is in Google Cloud Console
- Ensure cookies are enabled in your browser

---

## Future Enhancements

Possible additions:
- Map visualization with pothole locations
- Bulk update of impact scores
- Role-based access control (admin/viewer)
- Email notifications for high-impact potholes
- Mobile app integration
- Real-time data streaming

