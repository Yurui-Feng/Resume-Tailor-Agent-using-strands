/**
 * Resume Tailor Frontend Application
 */

// API Base URL
const API_BASE = '/api';

// Global state
let currentJobId = null;
let statusCheckInterval = null;

// DOM Elements
const elements = {
    // Form elements
    tailorForm: document.getElementById('tailorForm'),
    resumeSelect: document.getElementById('resumeSelect'),
    jobPosting: document.getElementById('jobPosting'),
    includeExperience: document.getElementById('includeExperience'),
    renderPdf: document.getElementById('renderPdf'),
    submitBtn: document.getElementById('submitBtn'),
    uploadBtn: document.getElementById('uploadBtn'),
    fileInput: document.getElementById('fileInput'),

    // Status elements
    charCount: document.getElementById('charCount'),
    validationMsg: document.getElementById('validationMsg'),
    apiStatus: document.getElementById('api-status'),

    // Processing section
    processingSection: document.getElementById('processingSection'),
    progressBar: document.getElementById('progressBar'),
    progressText: document.getElementById('progressText'),
    progressPercent: document.getElementById('progressPercent'),
    cancelBtn: document.getElementById('cancelBtn'),

    // Results section
    resultsSection: document.getElementById('resultsSection'),
    resultCompany: document.getElementById('resultCompany'),
    resultPosition: document.getElementById('resultPosition'),
    downloadTexBtn: document.getElementById('downloadTexBtn'),
    downloadPdfBtn: document.getElementById('downloadPdfBtn'),
    newJobBtn: document.getElementById('newJobBtn'),

    // Error section
    errorSection: document.getElementById('errorSection'),
    errorMessage: document.getElementById('errorMessage'),
    retryBtn: document.getElementById('retryBtn'),

    // History
    historyList: document.getElementById('historyList')
};


/**
 * Initialize application
 */
async function init() {
    console.log('Initializing Resume Tailor...');

    // Check API health
    await checkApiHealth();

    // Load resumes
    await loadResumes();

    // Load history
    await loadHistory();

    // Setup event listeners
    setupEventListeners();

    console.log('✅ Application initialized');
}


/**
 * Check API health
 */
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        if (data.status === 'healthy' && data.models_available) {
            elements.apiStatus.innerHTML = '<i class="fas fa-circle text-green-500"></i> API Connected';
        } else {
            elements.apiStatus.innerHTML = '<i class="fas fa-circle text-yellow-500"></i> API Connected (Models Not Configured)';
        }
    } catch (error) {
        elements.apiStatus.innerHTML = '<i class="fas fa-circle text-red-500"></i> API Disconnected';
        console.error('API health check failed:', error);
    }
}


/**
 * Load available resumes
 */
async function loadResumes() {
    try {
        const response = await fetch(`${API_BASE}/resumes`);
        const resumes = await response.json();

        elements.resumeSelect.innerHTML = '';

        if (resumes.length === 0) {
            elements.resumeSelect.innerHTML = '<option value="">No resumes found - upload one</option>';
            return;
        }

        resumes.forEach(resume => {
            const option = document.createElement('option');
            option.value = resume.id;
            option.textContent = `${resume.filename} (${formatBytes(resume.size)})`;
            elements.resumeSelect.appendChild(option);
        });

        console.log(`Loaded ${resumes.length} resumes`);
    } catch (error) {
        console.error('Failed to load resumes:', error);
        elements.resumeSelect.innerHTML = '<option value="">Error loading resumes</option>';
    }
}


/**
 * Load results history
 */
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/results`);
        const results = await response.json();

        if (results.length === 0) {
            elements.historyList.innerHTML = '<p class="text-gray-500 text-sm">No tailored resumes yet</p>';
            return;
        }

        elements.historyList.innerHTML = results.map(result => `
            <div class="border border-gray-200 rounded-md p-4 hover:bg-gray-50 transition">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-medium text-gray-900">${escapeHtml(result.company)} - ${escapeHtml(result.position)}</h4>
                        <p class="text-sm text-gray-500">${formatDate(result.created_at)}</p>
                    </div>
                    <div class="flex space-x-2">
                        ${result.has_tex ? `<a href="${API_BASE}/results/${result.id}/tex" class="text-blue-600 hover:text-blue-800" title="Download .tex"><i class="fas fa-file-alt"></i></a>` : ''}
                        ${result.has_pdf ? `<a href="${API_BASE}/results/${result.id}/pdf" class="text-red-600 hover:text-red-800" title="Download .pdf"><i class="fas fa-file-pdf"></i></a>` : ''}
                        <button onclick="deleteResult('${result.id}')" class="text-gray-400 hover:text-red-600" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        console.log(`Loaded ${results.length} results`);
    } catch (error) {
        console.error('Failed to load history:', error);
        elements.historyList.innerHTML = '<p class="text-red-500 text-sm">Error loading history</p>';
    }
}


/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Form submission
    elements.tailorForm.addEventListener('submit', handleFormSubmit);

    // Character count
    elements.jobPosting.addEventListener('input', updateCharCount);

    // File upload
    elements.uploadBtn.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileUpload);

    // New job button
    elements.newJobBtn.addEventListener('click', resetForm);

    // Retry button
    elements.retryBtn.addEventListener('click', resetForm);

    // Cancel button
    elements.cancelBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to cancel this job?')) {
            stopStatusChecking();
            resetForm();
        }
    });
}


/**
 * Update character count
 */
function updateCharCount() {
    const length = elements.jobPosting.value.length;
    elements.charCount.textContent = `${length} characters`;

    if (length < 50) {
        elements.validationMsg.classList.remove('hidden');
        elements.submitBtn.disabled = true;
    } else {
        elements.validationMsg.classList.add('hidden');
        elements.submitBtn.disabled = false;
    }
}


/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    // Hide previous sections
    elements.resultsSection.classList.add('hidden');
    elements.errorSection.classList.add('hidden');

    // Get form data
    const resumeId = elements.resumeSelect.value;
    const jobPosting = elements.jobPosting.value.trim();
    const includeExperience = elements.includeExperience.checked;
    const renderPdf = elements.renderPdf.checked;

    // Validate
    if (!resumeId) {
        showError('Please select a resume');
        return;
    }

    if (jobPosting.length < 50) {
        showError('Job posting must be at least 50 characters');
        return;
    }

    // Submit job
    try {
        elements.submitBtn.disabled = true;
        elements.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';

        const response = await fetch(`${API_BASE}/tailor`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_posting: jobPosting,
                original_resume_id: resumeId,
                include_experience: includeExperience,
                render_pdf: renderPdf
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit job');
        }

        const data = await response.json();
        currentJobId = data.job_id;

        console.log(`Job submitted: ${currentJobId}`);

        // Show processing section
        showProcessing();

        // Start checking status
        startStatusChecking();

    } catch (error) {
        console.error('Submission error:', error);
        showError(error.message);
        elements.submitBtn.disabled = false;
        elements.submitBtn.innerHTML = '<i class="fas fa-magic"></i> Tailor Resume';
    }
}


/**
 * Start checking job status
 */
function startStatusChecking() {
    statusCheckInterval = setInterval(checkJobStatus, 2000); // Check every 2 seconds
    checkJobStatus(); // Check immediately
}


/**
 * Stop checking job status
 */
function stopStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}


/**
 * Check job status
 */
async function checkJobStatus() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`${API_BASE}/jobs/${currentJobId}/status`);

        if (!response.ok) {
            throw new Error('Failed to check status');
        }

        const data = await response.json();

        // Update progress
        updateProgress(data.progress, data.message);

        // Handle status
        if (data.status === 'completed') {
            stopStatusChecking();
            showResults(data.result);
            await loadHistory(); // Refresh history
        } else if (data.status === 'failed') {
            stopStatusChecking();
            showError(data.error || 'Job failed');
        }

    } catch (error) {
        console.error('Status check error:', error);
        // Continue checking
    }
}


/**
 * Show processing section
 */
function showProcessing() {
    elements.tailorForm.classList.add('opacity-50', 'pointer-events-none');
    elements.processingSection.classList.remove('hidden');
    updateProgress(0, 'Starting...');
}


/**
 * Update progress bar
 */
function updateProgress(percent, message) {
    elements.progressBar.style.width = `${percent}%`;
    elements.progressPercent.textContent = `${percent}%`;
    elements.progressText.textContent = message;
}


/**
 * Show results
 */
function showResults(result) {
    elements.processingSection.classList.add('hidden');
    elements.resultsSection.classList.remove('hidden');

    elements.resultCompany.textContent = result.company;
    elements.resultPosition.textContent = result.position;

    // Extract result ID from path (handles both / and \ separators)
    const resultId = result.tex_path ? result.tex_path.split(/[/\\]/).pop().replace('.tex', '') : '';

    elements.downloadTexBtn.href = `${API_BASE}/results/${resultId}/tex`;
    elements.downloadPdfBtn.href = result.pdf_path ? `${API_BASE}/results/${resultId}/pdf` : '#';
    elements.downloadPdfBtn.style.display = result.pdf_path ? 'block' : 'none';

    console.log('✅ Results displayed');
}


/**
 * Show error
 */
function showError(message) {
    elements.processingSection.classList.add('hidden');
    elements.errorSection.classList.remove('hidden');
    elements.errorMessage.textContent = message;
}


/**
 * Reset form
 */
function resetForm() {
    elements.tailorForm.classList.remove('opacity-50', 'pointer-events-none');
    elements.processingSection.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
    elements.errorSection.classList.add('hidden');

    elements.submitBtn.disabled = false;
    elements.submitBtn.innerHTML = '<i class="fas fa-magic"></i> Tailor Resume';

    currentJobId = null;
    stopStatusChecking();
}


/**
 * Handle file upload
 */
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.tex')) {
        alert('Please upload a .tex file');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        elements.uploadBtn.disabled = true;
        elements.uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';

        const response = await fetch(`${API_BASE}/resumes/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        console.log('Resume uploaded:', data);

        // Reload resumes
        await loadResumes();

        // Select the newly uploaded resume
        elements.resumeSelect.value = data.resume_id;

        alert('Resume uploaded successfully!');

    } catch (error) {
        console.error('Upload error:', error);
        alert(`Upload failed: ${error.message}`);
    } finally {
        elements.uploadBtn.disabled = false;
        elements.uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Upload New';
        elements.fileInput.value = '';
    }
}


/**
 * Delete a result
 */
async function deleteResult(resultId) {
    if (!confirm('Are you sure you want to delete this result?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/results/${resultId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        console.log(`Deleted result: ${resultId}`);
        await loadHistory(); // Refresh history

    } catch (error) {
        console.error('Delete error:', error);
        alert(`Failed to delete: ${error.message}`);
    }
}


/**
 * Utility: Format bytes
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}


/**
 * Utility: Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;

    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
}


/**
 * Utility: Escape HTML
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}


// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
