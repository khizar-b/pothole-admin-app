# 🛣️ AdminVision Panel - Pothole Admin App

Professional admin web application for managing pothole detection data with intelligent impact scoring and multi-vehicle impact analysis.

## ✨ Key Features

### Core Functionality
- ✅ Admin authentication with registration
- ✅ CSV file upload with automatic impact score calculation
- ✅ SQLite database storage
- ✅ Real-time pothole data management
- ✅ GPS location tracking and mapping

### Advanced Features (NEW)
- ✅ **Impact Score Calculator**: Automatic calculation of pothole impact severity
- ✅ **Dual Impact Analysis**: Separate impact ratings for bikes and cars
- ✅ **Enhanced Statistics**: Comprehensive dashboard with impact distribution
- ✅ **CSV Export**: Download records with calculated impact scores
- ✅ **Admin Registration**: Create new administrator accounts
- ✅ **Google Sign-In**: Optional OAuth 2.0 integration (configured)
- ✅ **Road-Inspired Design**: Professional grey theme matching infrastructure

## 📊 Impact Score System

### Calculation Formula
```
impact_score = (area_normalized * 0.6) + (confidence_score * 0.4)
```

### Impact Levels
- **0-30**: 🟢 Low Impact (Low for bikes, Low for cars)
- **31-60**: 🟡 Medium Impact (Medium for bikes, Medium for cars)
- **61-100**: 🔴 High Impact (High for bikes, High for cars)

**See [IMPACT_SCORE_REFERENCE.py](IMPACT_SCORE_REFERENCE.py) for detailed calculation examples.**

## Tech Stack
- **Frontend**: HTML5, CSS3 (grey theme), Vanilla JavaScript
- **Backend**: Python Flask, Flask-SQLAlchemy
- **Database**: SQLite (default)
- **Authentication**: JWT + Bcrypt (+ optional Google OAuth)

## Installation & Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

This creates the database schema and default admin account.

### 3. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 4. (Optional) Enable Google Sign-In
1. Create a Google Cloud Project
2. Generate OAuth 2.0 Client ID
3. Update `templates/register.html` with your Client ID
4. See [ENHANCEMENTS_GUIDE.md](ENHANCEMENTS_GUIDE.md) for detailed setup

## Default Login Credentials
- **Username**: `admin`
- **Password**: generated when you run `init_db.py` unless you set `ADMIN_PASSWORD`

⚠️ **Important**: Save the initial password from the terminal and change it after first login.

## Usage Guide

### Uploading Pothole Data

1. Log in with admin credentials
2. Navigate to "Upload CSV" section
3. Select a CSV file with required columns:
   - `image_name` (string)
   - `timestamp` (ISO datetime)
   - `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height` (floats)
   - `confidence_score` (0.0-1.0)
   - `latitude`, `longitude` (floats)

4. Click "Upload File"
5. Impact scores calculated automatically ✨

**See [sample_data_updated.csv](sample_data_updated.csv) for example format.**

### Viewing & Managing Records

- Browse all detected potholes with impact analysis
- Search by image name
- View impact scores and bike/car impact levels
- GPS coordinates for each pothole
- Delete individual records as needed

### Statistics Dashboard

The enhanced statistics page shows:
- **Total Records**: Count of all potholes
- **Average Confidence**: Mean detection confidence
- **Impact Distribution**: Count of high/medium/low impact potholes
- **Bike Impact Analysis**: Risk levels for cyclists
- **Car Impact Analysis**: Risk levels for vehicles
- **Top 5 Potholes**: Highest impact records requiring urgent attention

### Exporting Data

1. Go to Records section
2. Click "📥 Export with Impact Scores"
3. CSV file downloads with all records and calculated metrics
4. Perfect for sharing with maintenance teams

### Admin Registration

1. Click "Sign up here" on login page
2. Enter username, password, and email (optional)
3. Confirm password
4. New admin account created and ready to use

## API Documentation

### Authentication Endpoints

**POST /api/auth/login**
- Login with username/password
- Returns: JWT access token

**POST /api/auth/register**
- Create new admin account
- Body: `{username, password, email (optional)}`
- Returns: Success message

**GET /api/auth/verify**
- Verify JWT token validity
- Headers: `Authorization: Bearer {token}`

### Data Endpoints

**POST /api/upload-csv**
- Upload CSV file
- Auto-calculates impact scores
- Returns: Upload statistics

**GET /api/potholes**
- Retrieve pothole records with pagination
- Returns: Records with impact data

**DELETE /api/potholes/{id}**
- Delete specific pothole record

**GET /api/stats**
- Get comprehensive statistics
- Returns: Impact distribution, bike/car analysis, top potholes

**GET /api/export-csv**
- Export all records as CSV
- Returns: CSV file with impact scores

## Database Schema

### PotholeRecord Model
```python
id: Integer (Primary Key)
image_name: String
timestamp: DateTime
bbox_x, bbox_y, bbox_width, bbox_height: Float
confidence_score: Float (0.0-1.0)
impact_score: Float (0.0-100.0) [CALCULATED]
bike_impact: String ('low', 'medium', 'high') [CALCULATED]
car_impact: String ('low', 'medium', 'high') [CALCULATED]
latitude, longitude: Float
uploaded_at: DateTime
uploaded_by: String
```

## File Structure
```
pothole-admin-app/
├── app.py                          # Flask application
├── models.py                       # Database models
├── config.py                       # Configuration
├── init_db.py                      # Database initialization
├── utils.py                        # Impact score calculation
├── requirements.txt                # Python dependencies
├── ENHANCEMENT_SUMMARY.md          # Detailed changes
├── ENHANCEMENTS_GUIDE.md          # Setup guide
├── IMPACT_SCORE_REFERENCE.py      # Calculation reference
├── sample_data_updated.csv        # Example CSV format
├── routes/
│   ├── auth.py                    # Authentication endpoints
│   ├── upload.py                  # CSV upload & data endpoints
│   └── pages.py                   # Page routes
├── templates/
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   └── dashboard.html             # Admin dashboard
└── static/
    ├── css/
    │   └── style.css              # Styling (grey theme)
    └── js/
        ├── login.js               # Login functionality
        ├── register.js            # Registration functionality
        └── dashboard.js           # Dashboard features
```

## Troubleshooting

### Database Issues
```bash
# Reset database
python init_db.py
```

### Port Already in Use
```bash
# Change port in app.py or use:
python app.py --port 5001
```

### CSV Upload Fails
- Verify all required columns present
- Check confidence_score is 0.0-1.0 (not 0-100)
- Ensure timestamp is in ISO format
- No duplicate rows

### Static Files Not Loading
```bash
# Ensure CSS/JS files exist in static/ directory
# Restart Flask application
```

## Security Notes

- Change default admin credentials immediately
- Use strong passwords (min 6 characters)
- JWT tokens expire after 30 days
- All passwords are bcrypt hashed
- Enable HTTPS in production
- Validate all uploaded CSV data

## Performance

- Handles 1000+ records efficiently
- Pagination: 50 records per page
- Impact scores calculated in real-time
- Database indexes on key fields
- Optimized CSV export

## Future Enhancements

- 🗺️ Interactive map visualization
- 📱 Mobile app integration
- 📧 Email notifications for high-impact potholes
- 📈 Advanced analytics and trends
- 🔄 Bulk operations
- 👥 Role-based access control
- 🌐 Multi-language support

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, feature requests, or questions:
- Check [ENHANCEMENTS_GUIDE.md](ENHANCEMENTS_GUIDE.md)
- Review [IMPACT_SCORE_REFERENCE.py](IMPACT_SCORE_REFERENCE.py)
- Check application logs
- Review error messages in browser console

---

**Version**: 2.0 Enhanced with Impact Scoring  
**Last Updated**: January 2026  
**Status**: Production Ready ✅

**Setup Note**: The initial admin password is generated during `init_db.py` unless you set `ADMIN_PASSWORD`.

**Important**: Save the generated password and change it after first login!

## CSV Format
The CSV file should contain the following columns:
- `image_name`: Name of the pothole image
- `timestamp`: Date and time of detection
- `bbox_x`: Bounding box X coordinate
- `bbox_y`: Bounding box Y coordinate
- `bbox_width`: Bounding box width
- `bbox_height`: Bounding box height
- `confidence_score`: Detection confidence (0-1)
- `damage_type`: Type of damage detected
- `latitude`: GPS latitude
- `longitude`: GPS longitude
