// ==================== Configuration ====================
const API_BASE_URL = 'http://localhost:8000';

// ==================== DOM Elements ====================
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const imagePreview = document.getElementById('imagePreview');
const removeImageBtn = document.getElementById('removeImage');
const predictionForm = document.getElementById('predictionForm');
const predictBtn = document.getElementById('predictBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultsSection = document.getElementById('resultsSection');

// Form inputs
const yMinInput = document.getElementById('yMin');
const yMaxInput = document.getElementById('yMax');
const nPointsInput = document.getElementById('nPoints');
const riskProfileSelect = document.getElementById('riskProfile');
const horizonSelect = document.getElementById('horizon');

// Result elements
const trendBadge = document.getElementById('trendBadge');
const trendResult = document.getElementById('trendResult');
const confidenceText = document.getElementById('confidenceText');
const probDown = document.getElementById('probDown');
const probSideways = document.getElementById('probSideways');
const probUp = document.getElementById('probUp');
const barDown = document.getElementById('barDown');
const barSideways = document.getElementById('barSideways');
const barUp = document.getElementById('barUp');
const chatbotMessage = document.getElementById('chatbotMessage');
const seriesLength = document.getElementById('seriesLength');
const windowSize = document.getElementById('windowSize');
const fileName = document.getElementById('fileName');

// ==================== State ====================
let selectedFile = null;

// ==================== Drag and Drop Handlers ====================
dropZone.addEventListener('click', () => {
    fileInput.click();
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// ==================== File Handling ====================
function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        showNotification('Please select a valid image file (PNG or JPG)', 'error');
        return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification('File size must be less than 10MB', 'error');
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        dropZone.style.display = 'none';
        previewSection.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    dropZone.style.display = 'block';
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
});

// ==================== Form Submission ====================
predictionForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validate file
    if (!selectedFile) {
        showNotification('Please select a chart image first', 'error');
        return;
    }

    // Validate Y-axis values
    const yMin = parseFloat(yMinInput.value);
    const yMax = parseFloat(yMaxInput.value);

    if (isNaN(yMin) || isNaN(yMax)) {
        showNotification('Please enter valid Y-axis values', 'error');
        return;
    }

    if (yMax <= yMin) {
        showNotification('Y-axis Max must be greater than Y-axis Min', 'error');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('y_min', yMin);
    formData.append('y_max', yMax);
    formData.append('n_points', nPointsInput.value);
    formData.append('risk_profile', riskProfileSelect.value);
    formData.append('horizon', horizonSelect.value);

    // Show loading
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/predict_trend_from_image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Prediction failed');
        }

        const data = await response.json();
        displayResults(data);

        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);

    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to get prediction. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
});

// ==================== Display Results ====================
function displayResults(data) {
    const { trend, probabilities, chatbot_message, meta } = data;

    // Update trend badge
    trendBadge.textContent = trend;
    trendBadge.className = 'trend-badge ' + trend.toLowerCase();

    // Update main prediction
    trendResult.textContent = trend;
    trendResult.className = 'prediction-value ' + trend.toLowerCase();

    // Update confidence text
    const maxProb = Math.max(probabilities.Down, probabilities.Sideways, probabilities.Up);
    const confidence = getConfidenceText(maxProb);
    confidenceText.textContent = confidence;

    // Update probabilities
    updateProbability('Down', probabilities.Down);
    updateProbability('Sideways', probabilities.Sideways);
    updateProbability('Up', probabilities.Up);

    // Update chatbot message
    chatbotMessage.textContent = chatbot_message;

    // Update meta info
    seriesLength.textContent = meta.series_length;
    windowSize.textContent = meta.used_window_size;
    fileName.textContent = meta.file_name;

    // Show results
    resultsSection.style.display = 'block';
}

function updateProbability(type, value) {
    const percentage = (value * 100).toFixed(1);

    if (type === 'Down') {
        probDown.textContent = percentage + '%';
        barDown.style.width = percentage + '%';
    } else if (type === 'Sideways') {
        probSideways.textContent = percentage + '%';
        barSideways.style.width = percentage + '%';
    } else if (type === 'Up') {
        probUp.textContent = percentage + '%';
        barUp.style.width = percentage + '%';
    }
}

function getConfidenceText(probability) {
    if (probability >= 0.75) {
        return 'High confidence prediction';
    } else if (probability >= 0.55) {
        return 'Moderate confidence prediction';
    } else {
        return 'Low confidence - mixed signals';
    }
}

// ==================== Loading State ====================
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
    predictBtn.disabled = show;

    if (show) {
        predictBtn.innerHTML = `
            <span>Analyzing...</span>
            <div style="width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        `;
    } else {
        predictBtn.innerHTML = `
            <span>Analyze Trend</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }
}

// ==================== Notifications ====================
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' : 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        max-width: 400px;
        font-weight: 500;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
}

// Add notification animations to CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== Smooth Scrolling ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== API Health Check ====================
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            console.log('✅ API is running');
        }
    } catch (error) {
        console.warn('⚠️ API is not accessible. Make sure the backend is running on', API_BASE_URL);
        showNotification('Backend API is not running. Please start the API server.', 'error');
    }
}

// Check API health on page load
window.addEventListener('load', () => {
    checkAPIHealth();
});

// ==================== Intersection Observer for Animations ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards and steps
document.querySelectorAll('.feature-card, .step').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// ==================== Console Welcome Message ====================
console.log('%c🚀 Stock Trend AI', 'font-size: 24px; font-weight: bold; color: #667eea;');
console.log('%cPowered by LSTM Neural Networks', 'font-size: 14px; color: #764ba2;');
console.log('%cAPI Endpoint:', 'font-weight: bold;', API_BASE_URL);
