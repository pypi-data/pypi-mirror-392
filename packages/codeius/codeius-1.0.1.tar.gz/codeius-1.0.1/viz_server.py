"""
Data Visualization Tool
Plot code metrics, test coverage, or database query results using matplotlib
"""
from flask import Flask, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import json
import tempfile
import os

app = Flask(__name__)

def generate_plot(plot_type, data, title="Data Visualization", xlabel="X-axis", ylabel="Y-axis"):
    """Generate a plot based on the specified type and data"""
    plt.figure(figsize=(10, 6))
    
    if plot_type == 'bar':
        labels = [item[0] for item in data]
        values = [item[1] for item in data]
        plt.bar(labels, values)
    elif plot_type == 'line':
        x_values = [item[0] for item in data]
        y_values = [item[1] for item in data]
        plt.plot(x_values, y_values, marker='o')
    elif plot_type == 'pie':
        labels = [item[0] for item in data]
        values = [item[1] for item in data]
        plt.pie(values, labels=labels, autopct='%1.1f%%')
    elif plot_type == 'scatter':
        x_values = [item[0] for item in data]
        y_values = [item[1] for item in data]
        plt.scatter(x_values, y_values)
    else:
        # Default to bar chart
        labels = [item[0] for item in data if len(item) > 0]
        values = [item[1] for item in data if len(item) > 1]
        plt.bar(labels, values)
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot to a BytesIO object
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()
    
    # Encode the image to base64
    img_base64 = base64.b64encode(img_buffer.read()).decode()
    return img_base64

@app.route('/plot', methods=['POST'])
def plot():
    """Generate a plot based on the provided data"""
    try:
        plot_type = request.json.get('type', 'bar')
        data = request.json.get('data', [])
        title = request.json.get('title', 'Data Visualization')
        xlabel = request.json.get('xlabel', 'X-axis')
        ylabel = request.json.get('ylabel', 'Y-axis')
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate the plot
        plot_image = generate_plot(plot_type, data, title, xlabel, ylabel)
        
        return jsonify({
            'success': True,
            'plot': plot_image,
            'type': plot_type,
            'title': title
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/plot_metrics', methods=['POST'])
def plot_metrics():
    """Generate plots for code metrics"""
    try:
        metric_type = request.json.get('metric_type', 'coverage')
        
        if metric_type == 'coverage':
            # Simulated test coverage data over time
            data = [
                ['Jan', 45],
                ['Feb', 52],
                ['Mar', 68],
                ['Apr', 78],
                ['May', 85],
                ['Jun', 82],
                ['Jul', 90]
            ]
            title = "Test Coverage Over Time"
            xlabel = "Month"
            ylabel = "Coverage %"
        elif metric_type == 'complexity':
            # Simulated code complexity metrics
            data = [
                ['module_a', 5.2],
                ['module_b', 3.7],
                ['module_c', 8.1],
                ['module_d', 2.4],
                ['module_e', 6.9]
            ]
            title = "Code Complexity by Module"
            xlabel = "Module"
            ylabel = "Complexity Score"
        elif metric_type == 'size':
            # Simulated file size data
            data = [
                ['main.py', 1250],
                ['utils.py', 870],
                ['models.py', 2100],
                ['views.py', 1850],
                ['tests.py', 3200]
            ]
            title = "File Sizes (lines of code)"
            xlabel = "File"
            ylabel = "Lines of Code"
        else:
            return jsonify({'error': f'Unknown metric type: {metric_type}'}), 400
        
        # Generate the plot
        plot_image = generate_plot('bar', data, title, xlabel, ylabel)
        
        return jsonify({
            'success': True,
            'plot': plot_image,
            'metric_type': metric_type,
            'title': title
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/plot_database', methods=['POST'])
def plot_database():
    """Generate plots for database query results"""
    try:
        # Extract query results from the request
        query_results = request.json.get('query_results', [])
        labels = request.json.get('labels', [])
        title = request.json.get('title', 'Database Query Results')
        
        if not query_results or not labels or len(query_results) != len(labels):
            return jsonify({'error': 'Invalid data provided for database plotting'}), 400
        
        # Format data for plotting
        data = list(zip(labels, query_results))
        
        # Generate the plot
        plot_image = generate_plot('bar', data, title, 'Category', 'Value')
        
        return jsonify({
            'success': True,
            'plot': plot_image,
            'title': title
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=10200)