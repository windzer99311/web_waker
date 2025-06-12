import re
from urllib.parse import urlparse

def validate_url(url):
    """Validate if a string is a proper URL"""
    if not url:
        return False
    
    # Add http:// if no scheme is present
    if not url.startswith(('http://', 'https://')):
        return False
    
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False

def parse_weblist_file(content):
    """Parse weblist.txt file content and return list of valid URLs"""
    urls = []
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
        
        # Add http:// if no scheme is present
        if not line.startswith(('http://', 'https://')):
            line = 'http://' + line
        
        if validate_url(line):
            urls.append(line)
    
    return urls

def format_response_time(response_time):
    """Format response time for display"""
    if response_time is None:
        return 'N/A'
    
    if response_time < 1:
        return f'{response_time * 1000:.0f}ms'
    else:
        return f'{response_time:.2f}s'

def format_uptime_percentage(percentage):
    """Format uptime percentage with appropriate color class"""
    if percentage >= 99:
        return 'success'
    elif percentage >= 95:
        return 'warning'
    else:
        return 'danger'
