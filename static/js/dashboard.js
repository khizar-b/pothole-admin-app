// Dashboard functionality
let currentPage = 1;
let allRecords = [];

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    
    if (!token) {
        window.location.href = '/';
        return;
    }
    
    // Display username
    document.getElementById('username').textContent = username;
    
    // Initialize navigation
    initNavigation();
    
    // Initialize upload functionality
    initUpload();
    
    // Initialize logout
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Initialize refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadRecords);
    
    // Initialize delete duplicates button
    document.getElementById('deleteDuplicatesBtn').addEventListener('click', deleteDuplicates);
    
    // Initialize search
    document.getElementById('searchInput').addEventListener('input', filterRecords);
    
    // Initialize export button
    document.getElementById('exportBtn').addEventListener('click', exportRecords);
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetSection = this.getAttribute('data-section');
            
            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // Update active section
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(targetSection + 'Section').classList.add('active');
            
            // Update page title
            const titles = {
                'upload': 'Upload CSV File',
                'records': 'View Records',
                'stats': 'Statistics'
            };
            document.getElementById('pageTitle').textContent = titles[targetSection];
            
            // Load data for section
            if (targetSection === 'records') {
                loadRecords();
            } else if (targetSection === 'stats') {
                loadStats();
            }
        });
    });
}

function initUpload() {
    const fileInput = document.getElementById('csvFile');
    const fileName = document.getElementById('fileName');
    const uploadForm = document.getElementById('uploadForm');
    
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            fileName.textContent = this.files[0].name;
        } else {
            fileName.textContent = 'Choose CSV file';
        }
    });
    
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showResult('Please select a file', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Show progress
        document.getElementById('uploadProgress').style.display = 'block';
        document.getElementById('uploadResult').style.display = 'none';
        document.getElementById('uploadBtn').disabled = true;
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/upload-csv', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                let message = `✅ Success! ${data.records_added} records added out of ${data.total_rows} rows.`;
                if (data.errors && data.errors.length > 0) {
                    message += `\n\n⚠️ Warnings:\n${data.errors.slice(0, 5).join('\n')}`;
                    if (data.errors.length > 5) {
                        message += `\n... and ${data.errors.length - 5} more`;
                    }
                }
                showResult(message, 'success');
                
                // Reset form
                uploadForm.reset();
                fileName.textContent = 'Choose CSV file';
            } else {
                showResult(`❌ Error: ${data.error}`, 'error');
            }
        } catch (error) {
            showResult(`❌ Upload failed: ${error.message}`, 'error');
        } finally {
            document.getElementById('uploadProgress').style.display = 'none';
            document.getElementById('uploadBtn').disabled = false;
        }
    });
}

function showResult(message, type) {
    const resultDiv = document.getElementById('uploadResult');
    resultDiv.textContent = message;
    resultDiv.className = `result-message ${type}`;
    resultDiv.style.display = 'block';
}

async function loadRecords(page = 1) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/potholes?page=${page}&per_page=50`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentPage = data.page; // Update current page
            allRecords = data.records;
            displayRecords(allRecords);
            displayPagination(data.page, data.pages);
        } else {
            showNoData('Failed to load records');
        }
    } catch (error) {
        showNoData('Error loading records');
    }
}

function displayRecords(records) {
    const tbody = document.getElementById('recordsTableBody');
    
    if (records.length === 0) {
        showNoData('No records found');
        return;
    }
    
    tbody.innerHTML = records.map(record => `
        <tr>
            <td>${record.id}</td>
            <td>${record.image_name}</td>
            <td>${new Date(record.timestamp).toLocaleString()}</td>
            <td>${(record.confidence_score * 100).toFixed(1)}%</td>
            <td><strong>${record.impact_score.toFixed(1)}</strong></td>
            <td><span class="impact-badge impact-${record.bike_impact}">${record.bike_impact}</span></td>
            <td><span class="impact-badge impact-${record.car_impact}">${record.car_impact}</span></td>
            <td>${record.gps_location.latitude.toFixed(6)}, ${record.gps_location.longitude.toFixed(6)}</td>
            <td>
                <button class="btn-danger" onclick="deleteRecord(${record.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function showNoData(message) {
    const tbody = document.getElementById('recordsTableBody');
    tbody.innerHTML = `<tr><td colspan="9" class="no-data">${message}</td></tr>`;
}

function displayPagination(currentPage, totalPages) {
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let buttons = [];
    
    // Previous button
    if (currentPage > 1) {
        buttons.push(`<button onclick="loadRecords(${currentPage - 1})">Previous</button>`);
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            buttons.push(`<button class="active">${i}</button>`);
        } else if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            buttons.push(`<button onclick="loadRecords(${i})">${i}</button>`);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            buttons.push(`<span>...</span>`);
        }
    }
    
    // Next button
    if (currentPage < totalPages) {
        buttons.push(`<button onclick="loadRecords(${currentPage + 1})">Next</button>`);
    }
    
    pagination.innerHTML = buttons.join('');
}

function filterRecords() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    if (!searchTerm) {
        displayRecords(allRecords);
        return;
    }
    
    const filtered = allRecords.filter(record => 
        record.image_name.toLowerCase().includes(searchTerm)
    );
    
    displayRecords(filtered);
}

async function deleteRecord(id) {
    if (!confirm('Are you sure you want to delete this record?')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/potholes/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            loadRecords(currentPage);
        } else {
            alert('Failed to delete record');
        }
    } catch (error) {
        alert('Error deleting record');
    }
}

async function loadStats() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/stats', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Display basic stats
            document.getElementById('totalRecords').textContent = data.total_records;
            document.getElementById('avgConfidence').textContent = data.average_confidence_score.toFixed(1) + '%';
            
            // Display impact score distribution
            document.getElementById('highImpactCount').textContent = data.impact_score_distribution.high;
            document.getElementById('mediumImpactCount').textContent = data.impact_score_distribution.medium;
            document.getElementById('lowImpactCount').textContent = data.impact_score_distribution.low;
            
            // Display bike impact distribution
            document.getElementById('bikeHighCount').textContent = data.bike_impact_distribution.high;
            document.getElementById('bikeMediumCount').textContent = data.bike_impact_distribution.medium;
            document.getElementById('bikeLowCount').textContent = data.bike_impact_distribution.low;
            
            // Display car impact distribution
            document.getElementById('carHighCount').textContent = data.car_impact_distribution.high;
            document.getElementById('carMediumCount').textContent = data.car_impact_distribution.medium;
            document.getElementById('carLowCount').textContent = data.car_impact_distribution.low;
            
            // Display top impact potholes
            displayTopPotholes(data.top_impact_potholes);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function displayTopPotholes(potholes) {
    const tbody = document.getElementById('topPotholesBody');
    
    if (potholes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">No potholes found</td></tr>';
        return;
    }
    
    tbody.innerHTML = potholes.map(pothole => `
        <tr>
            <td>${pothole.id}</td>
            <td>${pothole.image_name}</td>
            <td><strong>${pothole.impact_score.toFixed(1)}</strong></td>
            <td>${(pothole.confidence_score * 100).toFixed(1)}%</td>
            <td><span class="impact-badge impact-${pothole.bike_impact}">${pothole.bike_impact}</span></td>
            <td><span class="impact-badge impact-${pothole.car_impact}">${pothole.car_impact}</span></td>
            <td>${pothole.latitude.toFixed(6)}, ${pothole.longitude.toFixed(6)}</td>
        </tr>
    `).join('');
}

async function exportRecords() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/export-csv', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Create a blob and download
            const blob = new Blob([data.csv_data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = data.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } else {
            alert('Failed to export records');
        }
    } catch (error) {
        alert('Error exporting records: ' + error.message);
    }
}

async function deleteDuplicates() {
    if (!confirm('Are you sure you want to delete duplicate records? This will keep the first occurrence of each image name and delete the rest.')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/delete-duplicates', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(data.message);
            loadRecords(currentPage); // Refresh the records view
        } else {
            const data = await response.json();
            alert('Failed to delete duplicates: ' + data.error);
        }
    } catch (error) {
        alert('Error deleting duplicates: ' + error.message);
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = '/';
}
