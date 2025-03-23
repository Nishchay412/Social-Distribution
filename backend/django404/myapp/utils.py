# utils.py

import requests
from django.conf import settings
from myapp.models import User

def get_node_config_for_user(username):
    """
    Retrieve the node configuration for a user based on their 'home_node' field.
    If the user is found locally, return the corresponding configuration from settings.NODE_CONFIG.
    If the user is not found, return None.
    
    Args:
        username (str): The username to look up.
    
    Returns:
        dict or None: The node configuration dictionary (e.g., {'url': ..., 'api_key': ...}) or None if not found.
    """
    try:
        user = User.objects.get(username=username)
        node_identifier = user.home_node  # e.g., "node1" or "node2"
        return settings.NODE_CONFIG.get(node_identifier)
    except User.DoesNotExist:
        return None

def send_remote_follow_request(target_username, sender):
    """
    Send a follow request to a remote node for the specified target user.
    
    This function looks up the target user's node configuration using their home_node field,
    constructs the appropriate endpoint URL, and sends an HTTP POST request with the sender's information.
    
    Args:
        target_username (str): The username of the user to be followed (target).
        sender (User): The user instance of the sender initiating the follow request.
    
    Returns:
        dict: The JSON response from the remote node, or an error dictionary.
    """
    node_config = get_node_config_for_user(target_username)
    if not node_config:
        return {"error": "Target node configuration not found."}
    
    endpoint = f"{node_config['url']}/create_follow_request/{target_username}/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {node_config['api_key']}"
    }
    payload = {
        "sender_username": sender.username,
        # You can include additional data here if needed
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
