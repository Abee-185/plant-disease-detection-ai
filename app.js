// ==========================================
// BIOLOGICAL SPRINKLER - DASHBOARD LOGIC
// AI-Based Plant Disease Detection System
// ==========================================

// Global State
let currentMode = 'auto';
let sprinklerActive = false;
let currentImage = null;
let analysisData = null;

// Disease Database (Mock AI - for demo purposes)
const diseaseDatabase = {
    tomato: [
        { name: 'Early Blight', severity: 65, fertilizer: 'Copper Fungicide', quantity: 'Medium (2-3 kg/acre)' },
        { name: 'Late Blight', severity: 85, fertilizer: 'Mancozeb', quantity: 'High (3-4 kg/acre)' },
        { name: 'Septoria Leaf Spot', severity: 45, fertilizer: 'Chlorothalonil', quantity: 'Low (1-2 kg/acre)' },
        { name: 'Healthy', severity: 10, fertilizer: 'NPK 20-20-20', quantity: 'Low (1 kg/acre)' }
    ],
    potato: [
        { name: 'Early Blight', severity: 70, fertilizer: 'Copper Fungicide', quantity: 'Medium (2-3 kg/acre)' },
        { name: 'Late Blight', severity: 90, fertilizer: 'Metalaxyl', quantity: 'High (3-5 kg/acre)' },
        { name: 'Healthy', severity: 5, fertilizer: 'NPK 19-19-19', quantity: 'Low (1 kg/acre)' }
    ]
};

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    checkAuthentication();
    initializeEventListeners();
    updateLastAction('System initialized');
});

// ==========================================
// AUTHENTICATION
// ==========================================
function checkAuthentication() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'login.html';
        return;
    }

    const userData = JSON.parse(user);
    document.getElementById('userName').textContent = userData.username || 'User';
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// ==========================================
// EVENT LISTENERS
// ==========================================
function initializeEventListeners() {
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Image Upload
    document.getElementById('uploadBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', handleFileSelect);

    // Image Capture (simulated with file upload for web)
    document.getElementById('captureBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    // Analyze Button
    document.getElementById('analyzeBtn').addEventListener('click', analyzeImage);

    // Mode Selection
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const mode = this.dataset.mode;
            switchMode(mode);
        });
    });

    // Manual Control Buttons
    document.getElementById('sprinklerOnBtn').addEventListener('click', () => activateSprinkler(true));
    document.getElementById('sprinklerOffBtn').addEventListener('click', () => activateSprinkler(false));
    document.getElementById('applySprayBtn').addEventListener('click', applyRecommendedSpray);

    // History Refresh Button
    document.getElementById('refreshHistoryBtn').addEventListener('click', loadAnalysisHistory);

    // Load history on page load
    loadAnalysisHistory();
}

// ==========================================
// IMAGE HANDLING
// ==========================================
let currentImageFile = null;  // Store the file object for API upload

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file (JPG, PNG)');
        return;
    }

    // Store file object for API upload
    currentImageFile = file;

    // Read and display image
    const reader = new FileReader();
    reader.onload = function (e) {
        currentImage = e.target.result;
        displayImage(currentImage);
        showAnalyzeButton();
        updateLastAction('Image uploaded');
    };
    reader.readAsDataURL(file);
}

function displayImage(imageSrc) {
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');

    imagePreview.src = imageSrc;
    imagePreview.classList.add('active');
    uploadPlaceholder.style.display = 'none';
}

function showAnalyzeButton() {
    document.getElementById('analyzeBtn').style.display = 'inline-flex';
}

// ==========================================
// DISEASE ANALYSIS - REAL AI API
// ==========================================
const API_URL = 'http://localhost:5000';  // Backend API URL

async function analyzeImage() {
    if (!currentImageFile) {
        alert('Please upload an image first');
        return;
    }

    // Show loading state
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = '🔄 Analyzing...';
    analyzeBtn.disabled = true;

    try {
        // Create FormData to send image
        const formData = new FormData();
        formData.append('image', currentImageFile);

        // Call backend API
        const response = await fetch(`${API_URL}/analyze-leaf`, {
            method: 'POST',
            body: formData
        });

        // Parse response
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Analysis failed');
        }

        // Map fertilizer recommendations based on disease
        const fertilizerMap = {
            'Early Blight': { name: 'Copper Fungicide', quantity: 'Medium (2-3 kg/acre)' },
            'Late Blight': { name: 'Mancozeb', quantity: 'High (3-4 kg/acre)' },
            'Healthy': { name: 'NPK 20-20-20', quantity: 'Low (1 kg/acre)' }
        };

        const fertilizer = fertilizerMap[result.disease] || { name: 'Balanced NPK', quantity: 'Medium (2 kg/acre)' };

        // Prepare analysis data
        analysisData = {
            crop: result.crop,
            disease: result.disease,
            severity: result.severity,
            confidence: result.confidence,
            fertilizer: fertilizer.name,
            quantity: fertilizer.quantity,
            isHealthy: result.severity < 20
        };

        // Display results
        displayAnalysisResults(analysisData);

        // Reset analyze button
        analyzeBtn.textContent = '✓ Analysis Complete';
        analyzeBtn.disabled = false;

        // Update last action
        updateLastAction(`AI detected ${result.crop} - ${result.disease} (${result.severity}%)`);

        // Refresh history to show latest analysis
        setTimeout(() => loadAnalysisHistory(), 500);

        // If in AUTO mode, trigger automatic spray
        if (currentMode === 'auto' && !analysisData.isHealthy) {
            setTimeout(() => autoSpray(analysisData), 1000);
        }

    } catch (error) {
        console.error('Analysis error:', error);

        // Show error to user
        alert(`Analysis failed: ${error.message}\n\nMake sure the backend server is running at ${API_URL}`);

        // Reset analyze button
        analyzeBtn.textContent = '🔍 Analyze Disease';
        analyzeBtn.disabled = false;

        updateLastAction('Analysis failed - check backend connection');
    }
}

function displayAnalysisResults(data) {
    // Show analysis section
    document.getElementById('analysisSection').style.display = 'block';
    document.getElementById('noAnalysis').style.display = 'none';

    // Update crop and disease info
    document.getElementById('cropType').textContent = capitalizeFirst(data.crop);
    document.getElementById('diseaseName').textContent = data.disease;

    // Update health badge
    const healthBadge = document.getElementById('healthBadge');
    if (data.isHealthy) {
        healthBadge.innerHTML = '<span class="badge badge-healthy">✓ Healthy</span>';
    } else {
        healthBadge.innerHTML = '<span class="badge badge-diseased">🦠 Diseased</span>';
    }

    // Update severity circle
    updateSeverityCircle(data.severity);

    // Update fertilizer recommendation
    displayFertilizerRecommendation(data);

    // Update auto mode info
    updateAutoModeInfo(data);
}

// ==========================================
// CIRCULAR SEVERITY INDICATOR
// ==========================================
function updateSeverityCircle(percentage) {
    const circle = document.getElementById('progressCircle');
    const percentageText = document.getElementById('severityPercentage');
    const severityLabel = document.getElementById('severityLabel');
    const severityCircle = document.getElementById('severityCircle');

    // Calculate circle properties
    const radius = 90;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    // Animate the circle
    circle.style.strokeDashoffset = offset;

    // Update percentage text with animation
    animateValue(percentageText, 0, percentage, 1500);

    // Determine severity level and color
    let severityClass = '';
    let severityText = '';

    if (percentage <= 20) {
        severityClass = 'severity-healthy';
        severityText = 'Healthy - No immediate action needed';
    } else if (percentage <= 50) {
        severityClass = 'severity-mild';
        severityText = 'Mild - Monitor closely';
    } else if (percentage <= 80) {
        severityClass = 'severity-moderate';
        severityText = 'Moderate - Treatment recommended';
    } else {
        severityClass = 'severity-severe';
        severityText = 'Severe - Immediate treatment required';
    }

    // Apply severity class
    severityCircle.className = `circular-progress ${severityClass}`;
    severityLabel.textContent = severityText;
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16); // 60 FPS
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + '%';
    }, 16);
}

// ==========================================
// FERTILIZER RECOMMENDATION
// ==========================================
function displayFertilizerRecommendation(data) {
    document.getElementById('fertilizerSection').style.display = 'block';
    document.getElementById('noFertilizer').style.display = 'none';

    document.getElementById('fertilizerName').textContent = data.fertilizer;
    document.getElementById('fertilizerQuantity').textContent = data.quantity;
}

// ==========================================
// MODE SWITCHING
// ==========================================
function switchMode(mode) {
    currentMode = mode;

    // Update button states
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        }
    });

    // Toggle content visibility
    if (mode === 'auto') {
        document.getElementById('autoModeContent').style.display = 'block';
        document.getElementById('manualModeContent').style.display = 'none';
        document.getElementById('currentMode').textContent = 'AUTO';
    } else {
        document.getElementById('autoModeContent').style.display = 'none';
        document.getElementById('manualModeContent').style.display = 'block';
        document.getElementById('currentMode').textContent = 'MANUAL';
    }

    updateLastAction(`Switched to ${mode.toUpperCase()} mode`);
}

// ==========================================
// AUTO MODE
// ==========================================
function updateAutoModeInfo(data) {
    const duration = calculateSprayDuration(data.severity);
    document.getElementById('sprayDuration').textContent = duration;
    document.getElementById('autoFertilizer').textContent = data.fertilizer;
}

function calculateSprayDuration(severity) {
    if (severity <= 20) return '2 minutes';
    if (severity <= 50) return '5 minutes';
    if (severity <= 80) return '8 minutes';
    return '12 minutes';
}

function autoSpray(data) {
    if (currentMode !== 'auto') return;

    activateSprinkler(true);
    const duration = calculateSprayDuration(data.severity);
    updateLastAction(`AUTO: Spraying ${data.fertilizer} for ${duration}`);

    // Auto turn off after duration (simulated)
    const durationMs = parseInt(duration) * 60000; // Convert minutes to ms (shortened for demo)
    setTimeout(() => {
        if (currentMode === 'auto') {
            activateSprinkler(false);
            updateLastAction('AUTO: Spray cycle completed');
        }
    }, 5000); // 5 seconds for demo
}

// ==========================================
// MANUAL CONTROL
// ==========================================
function activateSprinkler(state) {
    sprinklerActive = state;
    updateSprinklerStatus(state);

    const action = state ? 'activated' : 'deactivated';
    updateLastAction(`Sprinkler ${action}`);

    if (currentMode === 'manual') {
        showManualStatus(state ? '✓ Sprinkler is now ON' : '✓ Sprinkler is now OFF');
    }
}

function applyRecommendedSpray() {
    if (!analysisData) {
        showManualStatus('⚠️ Please analyze an image first to get recommendations');
        return;
    }

    activateSprinkler(true);
    showManualStatus(`✓ Applying ${analysisData.fertilizer} - ${analysisData.quantity}`);
    updateLastAction(`MANUAL: Applied ${analysisData.fertilizer}`);

    // Auto turn off after 5 seconds (demo)
    setTimeout(() => {
        activateSprinkler(false);
        showManualStatus('✓ Spray application completed');
    }, 5000);
}

function showManualStatus(message) {
    const statusDiv = document.getElementById('manualStatus');
    statusDiv.querySelector('p').textContent = message;
    statusDiv.style.display = 'block';

    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

// ==========================================
// SYSTEM STATUS UPDATES
// ==========================================
function updateSprinklerStatus(isActive) {
    const statusElement = document.getElementById('sprinklerStatus');

    if (isActive) {
        statusElement.innerHTML = `
            <span class="status-dot status-active"></span>
            <span>ON</span>
        `;
    } else {
        statusElement.innerHTML = `
            <span class="status-dot status-disconnected"></span>
            <span>OFF</span>
        `;
    }
}

function updateLastAction(action) {
    const timestamp = new Date().toLocaleTimeString();
    document.getElementById('lastAction').textContent = `${action} at ${timestamp}`;
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ==========================================
// DEMO HELPER - Auto-populate for testing
// ==========================================
function runDemo() {
    // This function can be called from console to run a quick demo
    console.log('Running demo...');

    // Simulate image upload
    setTimeout(() => {
        console.log('Simulating image upload...');
        currentImage = 'demo';
        showAnalyzeButton();
    }, 1000);

    // Simulate analysis
    setTimeout(() => {
        console.log('Running analysis...');
        document.getElementById('analyzeBtn').click();
    }, 2000);
}

// ==========================================
// ANALYSIS HISTORY & REPORTS
// ==========================================
async function loadAnalysisHistory() {
    try {
        // Fetch history from backend
        const response = await fetch(`${API_URL}/history?limit=10`);
        const data = await response.json();

        if (!data.success) {
            console.error('Failed to load history:', data.error);
            return;
        }

        const tbody = document.getElementById('historyTableBody');

        if (data.history && data.history.length > 0) {
            // Clear existing rows
            tbody.innerHTML = '';

            // Add rows for each record
            data.history.forEach(record => {
                const row = document.createElement('tr');

                // Format timestamp
                const timestamp = new Date(record.timestamp).toLocaleString('en-IN', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });

                // Determine status badge
                const isHealthy = record.severity < 20;
                const statusBadge = isHealthy
                    ? '<span class="badge badge-healthy">✓ Healthy</span>'
                    : '<span class="badge badge-diseased">🦠 Diseased</span>';

                // Severity color
                let severityColor = 'var(--healthy-green)';
                if (record.severity > 20 && record.severity <= 50) severityColor = 'var(--warning-yellow)';
                else if (record.severity > 50 && record.severity <= 80) severityColor = 'var(--warning-orange)';
                else if (record.severity > 80) severityColor = 'var(--severe-red)';

                row.innerHTML = `
                    <td>${timestamp}</td>
                    <td><strong>${record.crop_type}</strong></td>
                    <td>${record.disease_name}</td>
                    <td style="color: ${severityColor}; font-weight: 600;">${record.severity}%</td>
                    <td>${(record.confidence * 100).toFixed(1)}%</td>
                    <td>${statusBadge}</td>
                `;

                tbody.appendChild(row);
            });

            // Load and display statistics
            loadStatistics();
        } else {
            // Show no data message
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: var(--spacing-lg); color: var(--gray-500);">
                        No analysis history yet. Upload and analyze an image to see results here.
                    </td>
                </tr>
            `;
        }

    } catch (error) {
        console.error('Error loading history:', error);
        const tbody = document.getElementById('historyTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: var(--spacing-lg); color: var(--danger-red);">
                    Failed to load history. Make sure backend server is running.
                </td>
            </tr>
        `;
    }
}

async function loadStatistics() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();

        if (data.success && data.statistics) {
            const stats = data.statistics;

            // Update statistics display
            document.getElementById('totalAnalyses').textContent = stats.total_analyses;
            document.getElementById('healthyCount').textContent = stats.healthy_count;
            document.getElementById('diseasedCount').textContent = stats.diseased_count;
            document.getElementById('avgSeverity').textContent = `${stats.average_severity}%`;

            // Show stats section if there's data
            if (stats.total_analyses > 0) {
                document.getElementById('historyStats').style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Make runDemo available in console
window.runDemo = runDemo;

console.log('🌱 Biological Sprinkler Dashboard initialized');
console.log('💡 Tip: Type runDemo() in console to see a quick demonstration');

