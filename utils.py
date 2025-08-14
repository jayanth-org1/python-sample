"""
Utility functions for the Flask application.
"""

import json
from datetime import datetime
from typing import Dict, List, Any


def format_datetime(dt: datetime) -> str:
    """
    Format datetime object to a readable string.
    
    Args:
        dt: datetime object to format
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def validate_task_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate task data for creation or update.
    
    Args:
        data: Dictionary containing task data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"
    
    if 'title' in data and not isinstance(data['title'], str):
        return False, "Title must be a string"
    
    if 'title' in data and len(data['title'].strip()) == 0:
        return False, "Title cannot be empty"
    
    if 'completed' in data and not isinstance(data['completed'], bool):
        return False, "Completed must be a boolean"
    
    return True, ""


def generate_sample_weather_data() -> Dict[str, str]:
    """
    Generate sample weather data for demonstration.
    
    Returns:
        Dictionary containing weather information
    """
    return {
        "location": "Sample City",
        "temperature": "22°C",
        "condition": "Sunny",
        "humidity": "65%",
        "wind_speed": "10 km/h",
        "pressure": "1013 hPa"
    }


def save_data_to_file(data: List[Dict], filename: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: Name of the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False


def load_data_from_file(filename: str) -> List[Dict]:
    """
    Load data from a JSON file.
    
    Args:
        filename: Name of the file to load
        
    Returns:
        List of dictionaries containing the data
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading data: {e}")
        return []


def get_application_info() -> Dict[str, str]:
    """
    Get basic information about the application.
    
    Returns:
        Dictionary containing application information
    """
    return {
        "name": "Python Flask Sample App",
        "version": "1.0.0",
        "description": "A simple web application built with Flask",
        "author": "Python Developer",
        "created": "2024"
    }
