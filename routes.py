import csv
import io
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, make_response, send_file
from urllib.parse import urlparse
from app import app, db
from models import Website, MonitoringResult, MonitoringSettings
from utils import validate_url, parse_weblist_file

@app.route('/')
def dashboard():
    websites = Website.query.filter_by(is_active=True).all()
    total_websites = len(websites)
    online_websites = sum(1 for w in websites if w.latest_result and w.latest_result.is_up)
    
    # Get monitoring settings
    settings = MonitoringSettings.query.first()
    check_interval = settings.check_interval if settings else 30
    
    stats = {
        'total_websites': total_websites,
        'online_websites': online_websites,
        'offline_websites': total_websites - online_websites,
        'uptime_percentage': round((online_websites / total_websites * 100) if total_websites > 0 else 0, 2),
        'check_interval': check_interval
    }
    
    return render_template('dashboard.html', websites=websites, stats=stats)

@app.route('/websites')
def websites():
    websites = Website.query.all()
    return render_template('websites.html', websites=websites)

@app.route('/add_website', methods=['POST'])
def add_website():
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    
    if not name or not url:
        flash('Name and URL are required.', 'error')
        return redirect(url_for('websites'))
    
    if not validate_url(url):
        flash('Please enter a valid URL (must include http:// or https://).', 'error')
        return redirect(url_for('websites'))
    
    # Check if URL already exists
    existing = Website.query.filter_by(url=url).first()
    if existing:
        flash('This URL is already being monitored.', 'error')
        return redirect(url_for('websites'))
    
    website = Website(name=name, url=url)
    db.session.add(website)
    db.session.commit()
    
    flash(f'Website "{name}" added successfully!', 'success')
    return redirect(url_for('websites'))

@app.route('/edit_website/<int:website_id>', methods=['POST'])
def edit_website(website_id):
    website = Website.query.get_or_404(website_id)
    
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    
    if not name or not url:
        flash('Name and URL are required.', 'error')
        return redirect(url_for('websites'))
    
    if not validate_url(url):
        flash('Please enter a valid URL (must include http:// or https://).', 'error')
        return redirect(url_for('websites'))
    
    # Check if URL already exists (excluding current website)
    existing = Website.query.filter(Website.url == url, Website.id != website_id).first()
    if existing:
        flash('This URL is already being monitored by another entry.', 'error')
        return redirect(url_for('websites'))
    
    website.name = name
    website.url = url
    db.session.commit()
    
    flash(f'Website "{name}" updated successfully!', 'success')
    return redirect(url_for('websites'))

@app.route('/delete_website/<int:website_id>', methods=['POST'])
def delete_website(website_id):
    website = Website.query.get_or_404(website_id)
    website_name = website.name
    
    db.session.delete(website)
    db.session.commit()
    
    flash(f'Website "{website_name}" deleted successfully!', 'success')
    return redirect(url_for('websites'))

@app.route('/toggle_website/<int:website_id>', methods=['POST'])
def toggle_website(website_id):
    website = Website.query.get_or_404(website_id)
    website.is_active = not website.is_active
    db.session.commit()
    
    status = "activated" if website.is_active else "deactivated"
    flash(f'Website "{website.name}" {status} successfully!', 'success')
    return redirect(url_for('websites'))

@app.route('/upload_weblist', methods=['POST'])
def upload_weblist():
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('websites'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('websites'))
    
    if not file.filename.endswith('.txt'):
        flash('Please upload a .txt file.', 'error')
        return redirect(url_for('websites'))
    
    try:
        content = file.read().decode('utf-8')
        websites_data = parse_weblist_file(content)
        
        added_count = 0
        skipped_count = 0
        
        for url in websites_data:
            # Check if URL already exists
            existing = Website.query.filter_by(url=url).first()
            if existing:
                skipped_count += 1
                continue
            
            # Extract domain name for the website name
            parsed_url = urlparse(url)
            name = parsed_url.netloc or url
            
            website = Website(name=name, url=url)
            db.session.add(website)
            added_count += 1
        
        db.session.commit()
        
        message = f'Upload completed! Added {added_count} websites.'
        if skipped_count > 0:
            message += f' Skipped {skipped_count} duplicate URLs.'
        
        flash(message, 'success')
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
    
    return redirect(url_for('websites'))

@app.route('/download_results')
def download_results():
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Website Name', 'URL', 'Status', 'Status Code', 'Response Time (s)', 'Last Checked', 'Uptime %', 'Error Message'])
    
    # Write data for each website
    websites = Website.query.all()
    for website in websites:
        latest_result = website.latest_result
        if latest_result:
            status = 'Online' if latest_result.is_up else 'Offline'
            status_code = latest_result.status_code or 'N/A'
            response_time = f'{latest_result.response_time:.3f}' if latest_result.response_time else 'N/A'
            last_checked = latest_result.checked_at.strftime('%Y-%m-%d %H:%M:%S')
            error_message = latest_result.error_message or ''
        else:
            status = 'Not Checked'
            status_code = 'N/A'
            response_time = 'N/A'
            last_checked = 'Never'
            error_message = ''
        
        writer.writerow([
            website.name,
            website.url,
            status,
            status_code,
            response_time,
            last_checked,
            website.uptime_percentage,
            error_message
        ])
    
    # Create response
    output.seek(0)
    
    # Create a proper file-like object
    csv_data = output.getvalue()
    output.close()
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=uptime_monitoring_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/website_details/<int:website_id>')
def website_details(website_id):
    website = Website.query.get_or_404(website_id)
    results = MonitoringResult.query.filter_by(website_id=website_id).order_by(MonitoringResult.checked_at.desc()).limit(50).all()
    
    return render_template('website_details.html', website=website, results=results)

@app.route('/settings')
def settings():
    settings = MonitoringSettings.query.first()
    if not settings:
        # Create default settings if none exist
        settings = MonitoringSettings(check_interval=30)
        db.session.add(settings)
        db.session.commit()
    
    return render_template('settings.html', settings=settings)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    check_interval = request.form.get('check_interval', type=int)
    
    if not check_interval or check_interval < 5:
        flash('Check interval must be at least 5 seconds.', 'error')
        return redirect(url_for('settings'))
    
    if check_interval > 3600:
        flash('Check interval cannot be more than 1 hour (3600 seconds).', 'error')
        return redirect(url_for('settings'))
    
    settings = MonitoringSettings.query.first()
    if not settings:
        settings = MonitoringSettings()
        db.session.add(settings)
    
    settings.check_interval = check_interval
    settings.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Monitoring interval updated to {check_interval} seconds.', 'success')
    return redirect(url_for('settings'))

@app.route('/api/dashboard_data')
def api_dashboard_data():
    """API endpoint for real-time dashboard data"""
    websites = Website.query.filter_by(is_active=True).all()
    
    data = []
    for website in websites:
        latest = website.latest_result
        data.append({
            'id': website.id,
            'name': website.name,
            'url': website.url,
            'is_up': latest.is_up if latest else None,
            'status_code': latest.status_code if latest else None,
            'response_time': latest.response_time if latest else None,
            'last_checked': latest.checked_at.isoformat() if latest else None,
            'uptime_percentage': website.uptime_percentage,
            'error_message': latest.error_message if latest else None
        })
    
    return {'websites': data}

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    websites = Website.query.filter_by(is_active=True).all()
    total_websites = len(websites)
    online_websites = sum(1 for w in websites if w.latest_result and w.latest_result.is_up)
    
    settings = MonitoringSettings.query.first()
    check_interval = settings.check_interval if settings else 30
    
    return {
        'total_websites': total_websites,
        'online_websites': online_websites,
        'offline_websites': total_websites - online_websites,
        'uptime_percentage': round((online_websites / total_websites * 100) if total_websites > 0 else 0, 2),
        'check_interval': check_interval
    }
