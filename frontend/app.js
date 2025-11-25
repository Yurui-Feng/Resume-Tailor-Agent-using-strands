/**
 * Resume Tailor Frontend Application
 */

// API Base URL
const API_BASE = '/api';

// Global state
let currentJobId = null;
let statusCheckInterval = null;
let currentCoverLetterJobId = null;
let coverLetterStatusInterval = null;
let latestTailoredId = null;
let availableResumes = [];

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

    // Cover letter form + status
    coverLetterForm: document.getElementById('coverLetterForm'),
    coverUseTailored: document.getElementById('coverUseTailored'),
    coverRenderPdf: document.getElementById('coverRenderPdf'),
    coverSubmitBtn: document.getElementById('coverSubmitBtn'),
    coverProcessingSection: document.getElementById('coverProcessingSection'),
    coverProgressBar: document.getElementById('coverProgressBar'),
    coverProgressText: document.getElementById('coverProgressText'),
    coverProgressPercent: document.getElementById('coverProgressPercent'),
    coverCancelBtn: document.getElementById('coverCancelBtn'),
    coverResultsSection: document.getElementById('coverResultsSection'),
    coverResultCompany: document.getElementById('coverResultCompany'),
    coverResultPosition: document.getElementById('coverResultPosition'),
    coverLetterText: document.getElementById('coverLetterText'),
    coverDownloadTexBtn: document.getElementById('coverDownloadTexBtn'),
    coverDownloadPdfBtn: document.getElementById('coverDownloadPdfBtn'),
    coverDownloadTxtBtn: document.getElementById('coverDownloadTxtBtn'),
    coverNewJobBtn: document.getElementById('coverNewJobBtn'),
    coverErrorSection: document.getElementById('coverErrorSection'),
    coverErrorMessage: document.getElementById('coverErrorMessage'),
    coverRetryBtn: document.getElementById('coverRetryBtn'),
    copyCoverLetterBtn: document.getElementById('copyCoverLetterBtn'),

    // History
    resumeHistoryList: document.getElementById('resumeHistoryList'),
    coverHistoryList: document.getElementById('coverHistoryList')
};

function isResumeJobActive() {
    return Boolean(currentJobId && statusCheckInterval);
}

function isCoverLetterJobActive() {
    return Boolean(currentCoverLetterJobId && coverLetterStatusInterval);
}


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
    await loadResumeHistory();
    await loadCoverLetterHistory();

    // Setup event listeners
    setupEventListeners();

    console.log('Application initialized');
}


/**
 * Check API health
 */
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        if (data.status === 'healthy' && data.models_available) {
            elements.apiStatus.textContent = 'API Connected';
        } else {
            elements.apiStatus.textContent = 'API Connected (Models Not Configured)';
        }
    } catch (error) {
        elements.apiStatus.textContent = 'API Disconnected';
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
        availableResumes = resumes || [];

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
        availableResumes = [];
    }
}


/**
 * Load results history
 */
async function loadResumeHistory() {
    try {
        const response = await fetch(`${API_BASE}/results`);
        const results = await response.json();

    if (results.length === 0) {
        elements.resumeHistoryList.innerHTML = '<p class="text-gray-500 text-sm">No tailored resumes yet</p>';
        latestTailoredId = null;
        return;
    }

        elements.resumeHistoryList.innerHTML = results.map(result => `
            <div class="border border-gray-200 rounded-md p-4 hover:bg-gray-50 transition">
                <div class="flex flex-col gap-3">
                    <div>
                        <h4 class="font-medium text-gray-900">${escapeHtml(result.company)} - ${escapeHtml(result.position)}</h4>
                        <p class="text-sm text-gray-500">${formatDate(result.created_at)}</p>
                    </div>
                    <div class="flex flex-wrap gap-2 justify-end">
                        ${result.has_tex ? `<a href="${API_BASE}/results/${result.id}/tex" class="brutalist-button brutalist-button--mini brutalist-button--ghost" target="_blank" rel="noopener noreferrer">TEX</a>` : ''}
                        ${result.has_pdf ? `<a href="${API_BASE}/results/${result.id}/pdf" class="brutalist-button brutalist-button--mini brutalist-button--emerald" target="_blank" rel="noopener noreferrer">PDF</a>` : ''}
                        <button type="button" onclick="deleteResult('${result.id}')" class="brutalist-button brutalist-button--mini brutalist-button--crimson">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        latestTailoredId = results[0]?.id || null;
        if (!latestTailoredId && elements.coverUseTailored) {
            elements.coverUseTailored.checked = false;
        }
        console.log(`Loaded ${results.length} results`);
    } catch (error) {
        console.error('Failed to load history:', error);
        elements.resumeHistoryList.innerHTML = '<p class="text-red-500 text-sm">Error loading history</p>';
        latestTailoredId = null;
    }
}


/**
 * Load cover letter history
 */
async function loadCoverLetterHistory() {
    try {
        const response = await fetch(`${API_BASE}/cover-letter/results`);
        const results = await response.json();

        if (results.length === 0) {
            elements.coverHistoryList.innerHTML = '<p class="text-gray-500 text-sm">No cover letters yet</p>';
            return;
        }

        elements.coverHistoryList.innerHTML = results.map(result => `
            <div class="border border-gray-200 rounded-md p-4 hover:bg-gray-50 transition">
                <div class="flex flex-col gap-3">
                    <div>
                        <h4 class="font-medium text-gray-900">${escapeHtml(result.company)} - ${escapeHtml(result.position)}</h4>
                        <p class="text-sm text-gray-500">${formatDate(result.created_at)}</p>
                    </div>
                    <div class="flex flex-wrap gap-2 justify-end">
                        ${result.has_tex ? `<a href="${API_BASE}/cover-letter/results/${result.id}/tex" class="brutalist-button brutalist-button--mini brutalist-button--ghost" target="_blank" rel="noopener noreferrer">TEX</a>` : ''}
                        ${result.has_txt ? `<a href="${API_BASE}/cover-letter/results/${result.id}/text" class="brutalist-button brutalist-button--mini brutalist-button--butter" target="_blank" rel="noopener noreferrer">TEXT</a>` : ''}
                        ${result.has_pdf ? `<a href="${API_BASE}/cover-letter/results/${result.id}/pdf" class="brutalist-button brutalist-button--mini brutalist-button--emerald" target="_blank" rel="noopener noreferrer">PDF</a>` : ''}
                        <button type="button" onclick="deleteCoverLetter('${result.id}')" class="brutalist-button brutalist-button--mini brutalist-button--crimson">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        console.log(`Loaded ${results.length} cover letters`);
    } catch (error) {
        console.error('Failed to load cover letter history:', error);
        elements.coverHistoryList.innerHTML = '<p class="text-red-500 text-sm">Error loading cover letters</p>';
    }
}


/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Form submission
    elements.tailorForm.addEventListener('submit', handleFormSubmit);
    elements.coverLetterForm.addEventListener('submit', handleCoverLetterSubmit);

    // Character count
    elements.jobPosting.addEventListener('input', updateCharCount);

    // File upload
    elements.uploadBtn.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileUpload);

    // New job button
    elements.newJobBtn.addEventListener('click', resetForm);
    elements.coverNewJobBtn.addEventListener('click', resetCoverLetterForm);

    // Retry button
    elements.retryBtn.addEventListener('click', resetForm);
    elements.coverRetryBtn.addEventListener('click', resetCoverLetterForm);

    // Cancel button
    elements.cancelBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to cancel this job?')) {
            stopStatusChecking();
            resetForm();
        }
    });
    elements.coverCancelBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to cancel this cover letter job?')) {
            stopCoverLetterStatusChecking();
            resetCoverLetterForm();
        }
    });

    // Copy cover letter text
    elements.copyCoverLetterBtn.addEventListener('click', copyCoverLetterText);
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

    if (isCoverLetterJobActive()) {
        showError('Please finish or cancel the cover letter job before tailoring a resume.');
        return;
    }

    // Submit job
    try {
        elements.submitBtn.disabled = true;
        elements.submitBtn.textContent = 'Submitting...';

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
        elements.submitBtn.textContent = 'Tailor Resume';
    }
}


/**
 * Handle cover letter submission
 */
async function handleCoverLetterSubmit(e) {
    e.preventDefault();

    elements.coverResultsSection.classList.add('hidden');
    elements.coverErrorSection.classList.add('hidden');
    elements.coverLetterText.textContent = '';

    const resumeId = elements.resumeSelect ? elements.resumeSelect.value : (availableResumes[0]?.id || '');
    const useTailored = elements.coverUseTailored ? elements.coverUseTailored.checked : false;
    const tailoredId = useTailored ? latestTailoredId : null;
    const jobPosting = elements.jobPosting ? elements.jobPosting.value.trim() : '';
    const renderPdf = elements.coverRenderPdf.checked;

    if (!resumeId) {
        showCoverLetterError('Please select a resume');
        return;
    }

    if (isResumeJobActive()) {
        showCoverLetterError('Please finish or cancel the resume tailoring job before creating a cover letter.');
        return;
    }

    // Reuse main job posting; assume it already passed validation in the main form

    try {
        elements.coverSubmitBtn.disabled = true;
        elements.coverSubmitBtn.textContent = 'Submitting...';

        const response = await fetch(`${API_BASE}/cover-letter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_posting: jobPosting,
                original_resume_id: resumeId,
                tailored_result_id: tailoredId || null,
                render_pdf: renderPdf
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit cover letter job');
        }

        const data = await response.json();
        currentCoverLetterJobId = data.job_id;

        showCoverLetterProcessing();
        startCoverLetterStatusChecking();

    } catch (error) {
        console.error('Cover letter submission error:', error);
        showCoverLetterError(error.message);
        elements.coverSubmitBtn.disabled = false;
        elements.coverSubmitBtn.textContent = 'Create Cover Letter';
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

        if (response.status === 404) {
            stopStatusChecking();
            currentJobId = null;
            showError('Resume job not found. Please resubmit.');
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to check status');
        }

        const data = await response.json();

        // Update progress
        updateProgress(data.progress, data.message);

        // Handle status
        if (data.status === 'completed') {
            stopStatusChecking();
            currentJobId = null;
            showResults(data.result);
            await loadResumeHistory(); // Refresh history
        } else if (data.status === 'failed') {
            stopStatusChecking();
            currentJobId = null;
            showError(data.error || 'Job failed');
        }

    } catch (error) {
        console.error('Status check error:', error);
        // Continue checking
    }
}


/**
 * Start checking cover letter job status
 */
function startCoverLetterStatusChecking() {
    coverLetterStatusInterval = setInterval(checkCoverLetterStatus, 2000);
    checkCoverLetterStatus();
}


/**
 * Stop checking cover letter job status
 */
function stopCoverLetterStatusChecking() {
    if (coverLetterStatusInterval) {
        clearInterval(coverLetterStatusInterval);
        coverLetterStatusInterval = null;
    }
}


/**
 * Check cover letter job status
 */
async function checkCoverLetterStatus() {
    if (!currentCoverLetterJobId) return;

    try {
        const response = await fetch(`${API_BASE}/cover-letter/jobs/${currentCoverLetterJobId}/status`);

        if (response.status === 404) {
            stopCoverLetterStatusChecking();
            currentCoverLetterJobId = null;
            showCoverLetterError('Cover letter job not found. Please resubmit.');
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to check status');
        }

        const data = await response.json();

        updateCoverLetterProgress(data.progress, data.message);

        if (data.status === 'completed') {
            stopCoverLetterStatusChecking();
            currentCoverLetterJobId = null;
            showCoverLetterResults(data.result);
            await loadCoverLetterHistory();
        } else if (data.status === 'failed') {
            stopCoverLetterStatusChecking();
            currentCoverLetterJobId = null;
            showCoverLetterError(data.error || 'Job failed');
        }
    } catch (error) {
        console.error('Cover letter status check error:', error);
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

    // Reset submit button state
    elements.submitBtn.disabled = false;
    elements.submitBtn.textContent = 'Tailor Resume';

    elements.resultCompany.textContent = result.company;
    elements.resultPosition.textContent = result.position;

    // Extract result ID from path (handles both / and \ separators)
    const resultId = result.tex_path ? result.tex_path.split(/[/\\]/).pop().replace('.tex', '') : '';

    elements.downloadTexBtn.href = `${API_BASE}/results/${resultId}/tex`;
    elements.downloadPdfBtn.href = result.pdf_path ? `${API_BASE}/results/${resultId}/pdf` : '#';
    elements.downloadPdfBtn.style.display = result.pdf_path ? 'block' : 'none';

    console.log('Results displayed');
}


/**
 * Show error
 */
function showError(message) {
    elements.processingSection.classList.add('hidden');
    elements.errorSection.classList.remove('hidden');
    elements.errorMessage.textContent = message;

    // Reset submit button state
    elements.submitBtn.disabled = false;
    elements.submitBtn.textContent = 'Tailor Resume';
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
    elements.submitBtn.textContent = 'Tailor Resume';

    currentJobId = null;
    stopStatusChecking();
}


/**
 * Cover letter helpers
 */
function showCoverLetterProcessing() {
    elements.coverLetterForm.classList.add('opacity-50', 'pointer-events-none');
    elements.coverProcessingSection.classList.remove('hidden');
    updateCoverLetterProgress(0, 'Starting...');
}


function updateCoverLetterProgress(percent, message) {
    elements.coverProgressBar.style.width = `${percent}%`;
    elements.coverProgressPercent.textContent = `${percent}%`;
    elements.coverProgressText.textContent = message;
}


function showCoverLetterResults(result) {
    elements.coverProcessingSection.classList.add('hidden');
    elements.coverResultsSection.classList.remove('hidden');
    elements.coverLetterForm.classList.remove('opacity-50', 'pointer-events-none');

    elements.coverSubmitBtn.disabled = false;
    elements.coverSubmitBtn.textContent = 'Create Cover Letter';

    elements.coverResultCompany.textContent = result.company || '';
    elements.coverResultPosition.textContent = result.position || '';
    elements.coverLetterText.textContent = result.plain_text || '';

    const resultId = (result.tex_path || result.text_path || '').split(/[/\\]/).pop().replace(/\.(tex|txt)$/i, '');

    elements.coverDownloadTexBtn.href = result.tex_path ? `${API_BASE}/cover-letter/results/${resultId}/tex` : '#';
    elements.coverDownloadTexBtn.style.display = result.tex_path ? 'block' : 'none';
    elements.coverDownloadPdfBtn.href = result.pdf_path ? `${API_BASE}/cover-letter/results/${resultId}/pdf` : '#';
    elements.coverDownloadPdfBtn.style.display = result.pdf_path ? 'block' : 'none';
    elements.coverDownloadTxtBtn.href = result.text_path ? `${API_BASE}/cover-letter/results/${resultId}/text` : '#';
    elements.coverDownloadTxtBtn.style.display = result.text_path ? 'block' : 'none';

    console.log('Cover letter displayed');
}


function showCoverLetterError(message) {
    elements.coverProcessingSection.classList.add('hidden');
    elements.coverErrorSection.classList.remove('hidden');
    elements.coverErrorMessage.textContent = message;

    elements.coverSubmitBtn.disabled = false;
    elements.coverSubmitBtn.textContent = 'Create Cover Letter';
    elements.coverLetterForm.classList.remove('opacity-50', 'pointer-events-none');
}


function resetCoverLetterForm() {
    elements.coverLetterForm.classList.remove('opacity-50', 'pointer-events-none');
    elements.coverProcessingSection.classList.add('hidden');
    elements.coverResultsSection.classList.add('hidden');
    elements.coverErrorSection.classList.add('hidden');

    elements.coverSubmitBtn.disabled = false;
    elements.coverSubmitBtn.textContent = 'Create Cover Letter';

    updateCoverLetterProgress(0, 'Waiting to start...');

    if (elements.coverUseTailored) {
        elements.coverUseTailored.checked = true;
    }

    currentCoverLetterJobId = null;
    stopCoverLetterStatusChecking();
}


async function copyCoverLetterText() {
    const text = elements.coverLetterText.textContent || '';
    if (!text) return;

    try {
        await navigator.clipboard.writeText(text);
        elements.copyCoverLetterBtn.textContent = 'Copied';
        setTimeout(() => {
            elements.copyCoverLetterBtn.textContent = 'Copy';
        }, 1500);
    } catch (error) {
        console.error('Copy failed:', error);
        alert('Unable to copy text. Please copy manually.');
    }
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
        elements.uploadBtn.textContent = 'Uploading...';

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
        elements.uploadBtn.textContent = 'Upload New';
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
        await loadResumeHistory(); // Refresh history

    } catch (error) {
        console.error('Delete error:', error);
        alert(`Failed to delete: ${error.message}`);
    }
}


/**
 * Delete a cover letter result
 */
async function deleteCoverLetter(resultId) {
    if (!confirm('Are you sure you want to delete this cover letter?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/cover-letter/results/${resultId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        console.log(`Deleted cover letter: ${resultId}`);
        await loadCoverLetterHistory();

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
