import re
from urllib.parse import urlparse

def messenger_link(facebook_profile: str) -> str:
    """
    Build Facebook Messenger deep link from a facebook_profile field.
    
    Rules:
    - If facebook_profile has facebook.com/profile.php?id=NNN → use NNN
    - If it's facebook.com/<username> → use last path segment
    - If it's already a bare id/username → use as-is
    
    Returns: https://www.facebook.com/messages/t/<id-or-username>
    """
    if not facebook_profile:
        return ""
    
    profile = facebook_profile.strip()
    
    # If it's already a full messenger link, return as-is
    if 'facebook.com/messages/t/' in profile:
        return profile
    
    # Extract ID or username
    identifier = None
    
    # Case 1: profile.php?id=NNN
    if 'profile.php?id=' in profile:
        match = re.search(r'profile\.php\?id=([0-9]+)', profile)
        if match:
            identifier = match.group(1)
    
    # Case 2: facebook.com/<username> or just <username>
    elif 'facebook.com/' in profile:
        parsed = urlparse(profile if profile.startswith('http') else f'https://{profile}')
        path = parsed.path.strip('/')
        if path and not path.startswith('profile.php'):
            identifier = path
    
    # Case 3: bare username/id
    else:
        # Simple validation - no spaces, no special chars except dots, underscores, dashes
        if re.match(r'^[a-zA-Z0-9._-]+$', profile):
            identifier = profile
    
    if identifier:
        return f"https://www.facebook.com/messages/t/{identifier}"
    
    return ""