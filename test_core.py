#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_url_parsing():
    """Test URL parsing without pandas"""
    import re
    
    def parse_public_url(public_url):
        if not public_url:
            return None, None
        
        spreadsheet_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', public_url)
        if not spreadsheet_match:
            return None, None
        
        spreadsheet_id = spreadsheet_match.group(1)
        gid_match = re.search(r'[#?&]gid=([0-9]+)', public_url)
        gid = gid_match.group(1) if gid_match else '0'
        
        return spreadsheet_id, gid
    
    # Test parsing URL
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=123"
    spreadsheet_id, gid = parse_public_url(url)
    assert spreadsheet_id == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    assert gid == "123"
    print("✓ URL parsing works")

def test_messenger_links():
    """Test messenger link generation"""
    import re
    from urllib.parse import urlparse

    def messenger_link(facebook_profile):
        if not facebook_profile:
            return ""
        
        profile = facebook_profile.strip()
        
        if 'facebook.com/messages/t/' in profile:
            return profile
        
        identifier = None
        
        if 'profile.php?id=' in profile:
            match = re.search(r'profile\.php\?id=([0-9]+)', profile)
            if match:
                identifier = match.group(1)
        elif 'facebook.com/' in profile:
            parsed = urlparse(profile if profile.startswith('http') else f'https://{profile}')
            path = parsed.path.strip('/')
            if path and not path.startswith('profile.php'):
                identifier = path
        else:
            if re.match(r'^[a-zA-Z0-9._-]+$', profile):
                identifier = profile
        
        if identifier:
            return f"https://www.facebook.com/messages/t/{identifier}"
        
        return ""
    
    # Test messenger link generation
    profile = "https://www.facebook.com/profile.php?id=123456789"
    expected = "https://www.facebook.com/messages/t/123456789"
    assert messenger_link(profile) == expected
    print("✓ messenger_link profile.php works")
    
    profile = "john.smith"
    expected = "https://www.facebook.com/messages/t/john.smith"
    assert messenger_link(profile) == expected
    print("✓ messenger_link bare username works")

if __name__ == '__main__':
    print("Running core functionality tests...")
    test_url_parsing()
    test_messenger_links()
    print("Core functionality tests passed!")