import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_location_from_ip(ip_address):
    """Get location details from IP address"""
    try:
        if ip_address in ['127.0.0.1', 'localhost']:
            return {
                'city': 'Dhaka',
                'region': 'Dhaka Division',
                'country': 'Bangladesh'
            }
        
        # Using ipinfo.io service (free tier available)
        response = requests.get(f'https://ipinfo.io/{ip_address}?token={settings.IPINFO_TOKEN}')
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', ''),
                'region': data.get('region', ''),
                'country': data.get('country', '')
            }
    except Exception as e:
        logger.error(f"Error getting location from IP {ip_address}: {str(e)}")
    
    return {
        'city': '',
        'region': '',
        'country': ''
    }

def validate_bangladeshi_phone(phone):
    """Validate Bangladeshi phone number"""
    import re
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Check if it's 11 digits and starts with valid prefix
    if len(phone) != 11:
        return False
    
    valid_prefixes = ['013', '014', '015', '016', '017', '018', '019']
    return any(phone.startswith(prefix) for prefix in valid_prefixes)