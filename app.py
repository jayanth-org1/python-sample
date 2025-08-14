from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Sample data for demonstration
TASKS = [
    {"id": 1, "title": "Learn Flask", "completed": True},
    {"id": 2, "title": "Build a web app", "completed": False},
    {"id": 3, "title": "Deploy to production", "completed": False}
]

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html', tasks=TASKS, current_time=datetime.now())

@app.route('/api/tasks')
def get_tasks():
    """API endpoint to get all tasks"""
    return jsonify(TASKS)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """API endpoint to add a new task"""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    new_task = {
        "id": len(TASKS) + 1,
        "title": data['title'],
        "completed": False
    }
    TASKS.append(new_task)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """API endpoint to update a task"""
    task = next((t for t in TASKS if t['id'] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.get_json()
    if 'title' in data:
        task['title'] = data['title']
    if 'completed' in data:
        task['completed'] = data['completed']
    
    return jsonify(task)

@app.route('/api/weather')
def get_weather():
    """API endpoint to get weather information (mock data)"""
    weather_data = {
        "location": "Sample City",
        "temperature": "22°C",
        "condition": "Sunny",
        "humidity": "65%"
    }
    return jsonify(weather_data)

@app.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
