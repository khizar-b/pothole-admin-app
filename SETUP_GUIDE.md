# Pothole Admin App - Complete Setup Guide

## Project Overview
Admin web application for managing pothole detection data through CSV uploads.

**Tech Stack:** HTML/CSS/JavaScript, Python Flask, PostgreSQL

---

## Initial Setup (One-time only)

### 1. Database Setup
```sql
-- In PostgreSQL (SQL Shell - psql)
CREATE DATABASE pothole_db;
\c pothole_db
```

### 2. Environment Configuration
Update `.env` file with your credentials:
```
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/pothole_db
SECRET_KEY=change-this-secret
JWT_SECRET_KEY=change-this-jwt-secret
```

### 3. Install Dependencies
```powershell
cd C:\Users\HJ\Desktop\pothole-admin-app
C:\Users\HJ\Desktop\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Initialize Database
```powershell
C:\Users\HJ\Desktop\.venv\Scripts\python.exe init_db.py
```

---

## Running the App (Every time)

### Start the Server
```powershell
cd C:\Users\HJ\Desktop\pothole-admin-app
C:\Users\HJ\Desktop\.venv\Scripts\python.exe app.py
```

### Access the App
- **URL:** http://localhost:5000
- **Username:** admin
- **Password:** generated when you run `init_db.py` unless you set `ADMIN_PASSWORD`

---

## Project Structure

```
pothole-admin-app/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── init_db.py           # Database initialization
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── routes/
│   ├── auth.py         # Authentication endpoints
│   ├── upload.py       # CSV upload & data management
│   └── pages.py        # Page routes
├── static/
│   ├── css/style.css   # Styling
│   └── js/
│       ├── login.js    # Login functionality
│       └── dashboard.js # Dashboard functionality
├── templates/
│   ├── login.html      # Login page
│   └── dashboard.html  # Dashboard page
└── sample_data.csv     # Sample CSV for testing
```

---

## API Endpoints

### Authentication
- `POST /api/auth/login` - Admin login
- `GET /api/auth/verify` - Verify JWT token
- `POST /api/auth/change-password` - Change password

### Data Management
- `POST /api/upload-csv` - Upload CSV file
- `GET /api/potholes` - Get pothole records (paginated)
- `DELETE /api/potholes/:id` - Delete a record
- `GET /api/stats` - Get statistics

### Pages
- `GET /` - Login page
- `GET /dashboard` - Dashboard page
- `GET /health` - Health check endpoint

---

## CSV Format Requirements

Your CSV must contain these columns:
- `image_name` - Name of the pothole image
- `timestamp` - Date and time of detection
- `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height` - Bounding box coordinates
- `confidence_score` - Detection confidence (0-1)
- `damage_type` - Type of damage detected
- `latitude`, `longitude` - GPS coordinates

**Example:**
```csv
image_name,timestamp,bbox_x,bbox_y,bbox_width,bbox_height,confidence_score,damage_type,latitude,longitude
pothole_001.jpg,2025-12-19 10:30:00,120,150,80,60,0.95,Crack,40.7128,-74.0060
```

---

## Troubleshooting

### Port Already in Use
```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <process_id> /F
```

### Database Connection Error
1. Verify PostgreSQL is running
2. Check `.env` DATABASE_URL is correct
3. Ensure `pothole_db` database exists

### Module Not Found Errors
```powershell
# Reinstall dependencies
C:\Users\HJ\Desktop\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Tables Don't Exist
```powershell
# Re-initialize database
C:\Users\HJ\Desktop\.venv\Scripts\python.exe init_db.py
```

---

## Important Notes

1. **Save the Initial Password:** The first admin password is generated during setup unless `ADMIN_PASSWORD` is set
2. **Database Location:** PostgreSQL stores data separately from the app folder
3. **Backup:** Copy the entire `pothole-admin-app` folder to backup your code
4. **PostgreSQL Data:** Use `pg_dump` to backup database:
   ```powershell
   pg_dump -U postgres pothole_db > backup.sql
   ```

---

## Future Enhancements (Ideas)

- Add user roles (admin, viewer)
- Export data to CSV
- Image upload for potholes
- Map view with GPS coordinates
- Advanced filtering and search
- Email notifications
- API key authentication for external apps

---

## Support

If you encounter issues:
1. Check the terminal/console for error messages
2. Verify all services (PostgreSQL) are running
3. Ensure virtual environment is activated
4. Check firewall settings for port 5000

---

**Created:** December 19, 2025
**Python Version:** 3.14.0
**Virtual Environment:** C:\Users\HJ\Desktop\.venv
