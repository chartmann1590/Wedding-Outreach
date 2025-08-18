import requests
import json
from typing import Optional, Dict, List, Tuple

def draft_message(friend_name: str, ollama_base_url: str, ollama_model: str, wedding_details: dict = None, timeout: int = 10) -> str:
    """
    Draft a friendly message using Ollama API.
    
    Args:
        friend_name: Name of the friend to message
        ollama_base_url: Ollama server base URL
        ollama_model: Model name to use
        timeout: Request timeout in seconds
    
    Returns:
        Generated message or fallback text if API fails
    """
    # Get wedding details or use defaults
    if wedding_details:
        bride_name = wedding_details.get('bride_name', 'Jessica')
        groom_name = wedding_details.get('groom_name', 'Charles')
        wedding_date = wedding_details.get('wedding_date', '')
        message_sender = wedding_details.get('message_sender', 'both')
    else:
        bride_name = 'Jessica'
        groom_name = 'Charles'
        wedding_date = ''
        message_sender = 'both'
    
    # Determine couple name and sender
    if message_sender == 'bride':
        couple_name = bride_name
        sender_sig = bride_name
    elif message_sender == 'groom':
        couple_name = groom_name
        sender_sig = groom_name
    else:  # both
        couple_name = f"{groom_name} & {bride_name}"
        sender_sig = f"{groom_name} & {bride_name}"
    
    # Create unique fallback messages for each person (no dates, no signatures)
    import random
    import hashlib
    
    # Use name to generate consistent but unique fallback
    name_seed = int(hashlib.md5(friend_name.lower().encode()).hexdigest()[:8], 16)
    name_rng = random.Random(name_seed)
    
    fallback_options = [
        f"Hey {friend_name}! Need your address for our save the date card. Where should I send this romantic chaos?",
        f"Yo {friend_name}! Got a save the date with your name on it - where do I aim this love missile?",
        f"{friend_name}, holding our save the date hostage until you give me your address!",
        f"Quick {friend_name}! Save the date needs a destination. What are your mailing coordinates?",
        f"Address alert {friend_name}! Save the date deployment requires your location!",
        f"Psst {friend_name}... got any good addresses? Asking for a save the date card.",
        f"{friend_name}, the mailman is asking about you. Where does he find the legendary {friend_name} for our save the date?",
        f"URGENT {friend_name}! Save the date emergency. Deploy your address immediately!",
        f"{friend_name}, my save the date is lost without your address. Save it from the postal wilderness!",
        f"Listen {friend_name}, assembled a team of carrier pigeons for our save the date. Save them the trip - address please?",
        f"Breaking news {friend_name}: Address needed for top secret save the date mission!",
        f"{friend_name}! Address detective here. Need your location for save the date crimes!",
        f"Warning {friend_name}: Fancy save the date paper incoming! Coordinates required!",
        f"Help {friend_name}! Where should this save the date find you hiding?",
        f"{friend_name}, if a save the date were to magically appear, where would it land?",
        f"Attention {friend_name}! Save the date alert system activated. Please provide target coordinates!",
        f"{friend_name}, our save the date is having an identity crisis without your address!",
        f"Mission impossible {friend_name}: Deliver save the date to mysterious location. Need intel!",
        f"{friend_name}! Save the date carrier pigeon union is on strike. Regular mail address needed!",
        f"Emergency broadcast {friend_name}: Save the date requires immediate address extraction!"
    ]
    
    fallback_message = name_rng.choice(fallback_options)
    
    if not ollama_base_url or not ollama_model:
        return fallback_message
    
    try:
        # Ensure URL ends with /api/generate
        base_url = ollama_base_url.rstrip('/')
        if not base_url.endswith('/api/generate'):
            base_url += '/api/generate'
        
        # Add randomization to ensure unique messages
        import random
        import time
        random.seed(int(time.time() * 1000) + hash(friend_name))
        
        styles = [
            "super casual and funny",
            "playfully dramatic",
            "hilariously over-the-top",
            "charmingly silly",
            "witty and clever",
            "goofily enthusiastic",
            "sarcastically sweet"
        ]
        
        scenarios = [
            "save the date emergency",
            "address collection mission",
            "fancy save the date delivery quest",
            "mailbox invasion plan",
            "save the date distribution operation"
        ]
        
        chosen_style = random.choice(styles)
        chosen_scenario = random.choice(scenarios)
        randomizer = random.randint(1000, 9999)
        
        date_info = f" on {wedding_date}" if wedding_date else ""
        
        prompt = f"""You are writing message #{randomizer} for {friend_name}. Be {chosen_style} about this {chosen_scenario}.

        CRITICAL: This message must be COMPLETELY DIFFERENT from any previous message. Be creative and original!
        
        Write a unique, funny message to {friend_name} asking for their address for a save the date card.
        
        Requirements:
        - Make it {chosen_style} and totally unique 
        - Use ONLY {friend_name}'s FIRST NAME
        - Keep under 30 words
        - Be playful about the {chosen_scenario}
        - Try wordplay or puns with "{friend_name}" if possible
        - NO emojis (text only)
        - NO signatures or names at the end
        - NO mention of specific dates or couple names
        - NO quotation marks anywhere in the message
        - Make it sound like YOU are asking for the address
        - Mention it's for a save the date card in a funny way
        
        Different approaches to try:
        - Rhyming messages with {friend_name}
        - Alliteration with their name
        - Funny analogies 
        - Silly threats (like carrier pigeons)
        - Over-dramatic pleas
        - Clever wordplay with {friend_name}
        - Random humor styles
        
        Make this message #{randomizer} completely unique and personal for {friend_name}:"""
        
        payload = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 1.2,  # Higher temperature for more creativity
                "top_p": 0.95,
                "top_k": 50,
                "repeat_penalty": 1.3,  # Prevent repetitive responses
                "seed": randomizer  # Use random seed for each person
            }
        }
        
        response = requests.post(
            base_url,
            json=payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            # Clean up the text - remove emojis and problematic unicode characters
            import re
            # Remove emoji and other unicode symbols, keep only basic text
            generated_text = re.sub(r'[^\x00-\x7F]+', '', generated_text)
            generated_text = generated_text.strip()
            
            # Basic validation - ensure message isn't too long or empty
            if generated_text and len(generated_text) < 200:
                return generated_text
        
        return fallback_message
        
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        return fallback_message

def test_ollama_connection(ollama_base_url: str, timeout: int = 5) -> Tuple[bool, str]:
    """
    Test connection to Ollama server.
    
    Args:
        ollama_base_url: Ollama server base URL
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not ollama_base_url:
        return False, "No Ollama base URL provided"
    
    try:
        base_url = ollama_base_url.rstrip('/')
        health_url = f"{base_url}/api/tags"
        
        response = requests.get(health_url, timeout=timeout)
        
        if response.status_code == 200:
            return True, "Connection successful"
        else:
            return False, f"Server responded with status {response.status_code}"
            
    except requests.exceptions.ConnectTimeout:
        return False, "Connection timeout - server may be down"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server - check URL and ensure Ollama is running"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def get_available_models(ollama_base_url: str, timeout: int = 10) -> Tuple[bool, List[str], str]:
    """
    Get list of available models from Ollama server.
    
    Args:
        ollama_base_url: Ollama server base URL
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (success: bool, models: List[str], error_message: str)
    """
    if not ollama_base_url:
        return False, [], "No Ollama base URL provided"
    
    try:
        base_url = ollama_base_url.rstrip('/')
        models_url = f"{base_url}/api/tags"
        
        response = requests.get(models_url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            models = []
            
            for model in data.get('models', []):
                model_name = model.get('name', '')
                if model_name:
                    # Remove tag suffix for cleaner display
                    clean_name = model_name.split(':')[0]
                    if clean_name not in models:
                        models.append(clean_name)
            
            return True, sorted(models), ""
        else:
            return False, [], f"Server responded with status {response.status_code}"
            
    except requests.exceptions.ConnectTimeout:
        return False, [], "Connection timeout - server may be down"
    except requests.exceptions.ConnectionError:
        return False, [], "Cannot connect to server - check URL and ensure Ollama is running"
    except Exception as e:
        return False, [], f"Error fetching models: {str(e)}"

def pull_model(ollama_base_url: str, model_name: str, timeout: int = 300) -> Tuple[bool, str]:
    """
    Pull/download a model from Ollama.
    
    Args:
        ollama_base_url: Ollama server base URL
        model_name: Name of model to pull
        timeout: Request timeout in seconds (default 5 minutes)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not ollama_base_url or not model_name:
        return False, "Missing base URL or model name"
    
    try:
        base_url = ollama_base_url.rstrip('/')
        pull_url = f"{base_url}/api/pull"
        
        payload = {
            "name": model_name,
            "stream": False
        }
        
        response = requests.post(
            pull_url,
            json=payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return True, f"Successfully pulled model '{model_name}'"
        else:
            return False, f"Failed to pull model: status {response.status_code}"
            
    except requests.exceptions.ConnectTimeout:
        return False, "Pull operation timed out - large models can take several minutes"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server - check URL and ensure Ollama is running"
    except Exception as e:
        return False, f"Error pulling model: {str(e)}"

def test_model_generate(ollama_base_url: str, model_name: str, timeout: int = 30) -> Tuple[bool, str]:
    """
    Test if a model can generate text.
    
    Args:
        ollama_base_url: Ollama server base URL
        model_name: Name of model to test
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not ollama_base_url or not model_name:
        return False, "Missing base URL or model name"
    
    try:
        base_url = ollama_base_url.rstrip('/')
        if not base_url.endswith('/api/generate'):
            base_url += '/api/generate'
        
        payload = {
            "model": model_name,
            "prompt": "Hello, can you generate a simple greeting?",
            "stream": False,
            "options": {"temperature": 0.1}
        }
        
        response = requests.post(
            base_url,
            json=payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            if generated_text:
                return True, f"Model '{model_name}' is working correctly"
            else:
                return False, f"Model '{model_name}' returned empty response"
        else:
            return False, f"Model test failed: status {response.status_code}"
            
    except requests.exceptions.ConnectTimeout:
        return False, "Model test timed out - model may not be loaded"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server"
    except Exception as e:
        return False, f"Error testing model: {str(e)}"