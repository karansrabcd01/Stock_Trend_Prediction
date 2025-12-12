# Stock Trend AI - Frontend

A stunning, modern web interface for the Stock Trend Prediction API. Upload stock chart screenshots and get AI-powered trend predictions with personalized insights.

## ✨ Features

- **🎨 Premium Design**: Modern UI with glassmorphism, gradients, and smooth animations
- **📤 Drag & Drop**: Easy file upload with drag-and-drop support
- **📊 Real-time Predictions**: Instant AI-powered trend analysis
- **💡 Smart Insights**: Personalized recommendations based on risk profile
- **📱 Responsive**: Works perfectly on all devices
- **⚡ Fast**: Optimized performance with smooth interactions

## 🚀 Getting Started

### Prerequisites

Make sure your Stock Trend API backend is running on `http://localhost:8000`

### Running the Frontend

You have several options to run the frontend:

#### Option 1: Using Python's Built-in Server (Recommended)

```bash
# Navigate to the frontend directory
cd "c:\Users\HP\Desktop\KSR_Stock\frontend part"

# Start a simple HTTP server
python -m http.server 8080
```

Then open your browser and go to: `http://localhost:8080`

#### Option 2: Using Live Server (VS Code Extension)

1. Install the "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

#### Option 3: Direct File Opening

Simply double-click `index.html` to open it in your browser.

**Note**: Some browsers may block API requests when opening files directly. Using a local server (Options 1 or 2) is recommended.

## 📖 How to Use

1. **Upload Chart**: Drag and drop or click to select your stock chart screenshot
2. **Configure Settings**:
   - Set Y-axis minimum and maximum values
   - Choose number of sample points (default: 300)
   - Select your risk profile (Low/Medium/High)
   - Choose investment horizon (Short/Medium/Long)
3. **Analyze**: Click "Analyze Trend" to get predictions
4. **View Results**: See the predicted trend, probability breakdown, and AI insights

## 🎯 API Configuration

The frontend is configured to connect to the API at `http://localhost:8000`. If your API is running on a different port or host, update the `API_BASE_URL` in `script.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 🎨 Design Features

- **Dark Theme**: Easy on the eyes with vibrant accent colors
- **Glassmorphism**: Modern frosted glass effect on cards
- **Smooth Animations**: Engaging micro-interactions throughout
- **Gradient Accents**: Beautiful color transitions
- **Responsive Layout**: Adapts to any screen size

## 📁 File Structure

```
frontend part/
├── index.html      # Main HTML structure
├── styles.css      # Complete styling with animations
├── script.js       # JavaScript for interactions and API calls
└── README.md       # This file
```

## 🔧 Customization

### Changing Colors

Edit the CSS variables in `styles.css`:

```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    /* ... more variables */
}
```

### Modifying API Endpoint

Update `API_BASE_URL` in `script.js`:

```javascript
const API_BASE_URL = 'http://your-api-url:port';
```

## 🐛 Troubleshooting

### API Connection Issues

If you see "Backend API is not running" error:
1. Make sure the backend API is running
2. Check that it's running on `http://localhost:8000`
3. Verify CORS is enabled in the backend

### File Upload Issues

If file upload doesn't work:
1. Check file format (PNG or JPG only)
2. Ensure file size is under 10MB
3. Try using a local server instead of opening the file directly

### Results Not Showing

If predictions don't display:
1. Open browser console (F12) to check for errors
2. Verify Y-axis min/max values are correct
3. Ensure the uploaded image is a valid chart

## 📝 Browser Support

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## 🎓 Tips for Best Results

1. **Chart Quality**: Use clear, high-contrast chart images
2. **Y-Axis Values**: Enter accurate min/max values from your chart
3. **Sample Points**: Higher values (500-1000) for more detailed analysis
4. **Risk Profile**: Choose based on your actual investment strategy

## 📄 License

This project is part of the Stock Trend Prediction system.

## 🤝 Support

For issues or questions, please check the main project documentation.

---

**Made with ❤️ using HTML, CSS, and Vanilla JavaScript**
