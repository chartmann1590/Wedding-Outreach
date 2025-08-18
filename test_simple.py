#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_sheets():
    from services.sheets import parse_public_url, to_csv_url
    
    # Test parsing URL
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=123"
    spreadsheet_id, gid = parse_public_url(url)
    assert spreadsheet_id == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    assert gid == "123"
    print("✓ sheets.parse_public_url works")
    
    # Test CSV URL generation
    csv_url = to_csv_url(spreadsheet_id, gid)
    expected = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/export?format=csv&gid=123"
    assert csv_url == expected
    print("✓ sheets.to_csv_url works")

def test_outreach():
    from services.outreach import messenger_link
    
    # Test messenger link generation
    profile = "https://www.facebook.com/profile.php?id=123456789"
    expected = "https://www.facebook.com/messages/t/123456789"
    assert messenger_link(profile) == expected
    print("✓ outreach.messenger_link works")
    
    profile = "john.smith"
    expected = "https://www.facebook.com/messages/t/john.smith"
    assert messenger_link(profile) == expected
    print("✓ outreach.messenger_link handles bare username")

def test_ollama():
    from services.ollama import draft_message
    
    # Test fallback message
    message = draft_message('John', '', '')
    assert 'John' in message
    assert 'Charles & Jessica' in message
    print("✓ ollama.draft_message fallback works")

if __name__ == '__main__':
    print("Running basic functionality tests...")
    test_sheets()
    test_outreach()
    test_ollama()
    print("All basic tests passed!")