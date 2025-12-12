import requests
import matplotlib.pyplot as plt
import numpy as np

# Generate a sample stock chart
def create_sample_chart(filename="test_chart.png"):
    """Create a simple upward trending stock chart"""
    # Generate sample data with upward trend
    np.random.seed(42)
    days = 100
    base_price = 100
    trend = np.linspace(0, 50, days)  # Upward trend
    noise = np.random.normal(0, 5, days)  # Random noise
    prices = base_price + trend + noise
    
    # Create the chart
    plt.figure(figsize=(10, 6))
    plt.plot(prices, color='black', linewidth=2)
    plt.ylim(80, 180)
    plt.xlim(0, days)
    plt.grid(True, alpha=0.3)
    plt.title("Sample Stock Chart")
    plt.xlabel("Days")
    plt.ylabel("Price")
    
    # Save with white background
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filename, 80, 180  # filename, y_min, y_max

# Test the API
def test_api():
    # Create sample chart
    chart_file, y_min, y_max = create_sample_chart()
    
    # API endpoint
    url = "http://localhost:8000/predict_trend_from_image"
    
    # Prepare the request
    with open(chart_file, 'rb') as f:
        files = {'file': (chart_file, f, 'image/png')}
        data = {
            'y_min': y_min,
            'y_max': y_max,
            'n_points': 300,
            'risk_profile': 'medium',
            'horizon': 'short'
        }
        
        # Send request
        print(f"Testing API with chart: {chart_file}")
        print(f"Y-axis range: {y_min} to {y_max}")
        print("\nSending request...")
        
        response = requests.post(url, files=files, data=data)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] API Response:")
        print(f"\nPredicted Trend: {result['trend']}")
        print(f"Confidence: {result['probabilities']}")
        print(f"\nChatbot Message:")
        print(result['chatbot_message'])
    else:
        print(f"\n[ERROR] Status code {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_api()
