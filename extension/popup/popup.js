/**
 * Popup Script for Resume Tailor Extension
 * Handles UI state, form submission, polling, and results display
 */

// DOM Elements
const elements = {
  // Views
  formView: document.getElementById('formView'),
  processingView: document.getElementById('processingView'),
  resultsView: document.getElementById('resultsView'),
  errorView: document.getElementById('errorView'),

  // Form elements
  scrapedNotice: document.getElementById('scrapedNotice'),
  jobPosting: document.getElementById('jobPosting'),
  charCount: document.getElementById('charCount'),
  resumeSelect: document.getElementById('resumeSelect'),
  includeExperience: document.getElementById('includeExperience'),
  renderPdf: document.getElementById('renderPdf'),
  submitBtn: document.getElementById('submitBtn'),

  // Processing elements
  progressBar: document.getElementById('progressBar'),
  progressPercent: document.getElementById('progressPercent'),
  progressText: document.getElementById('progressText'),
  terminalLogs: document.getElementById('terminalLogs'),
  cancelBtn: document.getElementById('cancelBtn'),

  // Results elements
  resultCompany: document.getElementById('resultCompany'),
  resultPosition: document.getElementById('resultPosition'),
  downloadTexBtn: document.getElementById('downloadTexBtn'),
  downloadPdfBtn: document.getElementById('downloadPdfBtn'),
  viewResultsBtn: document.getElementById('viewResultsBtn'),
  newJobBtn: document.getElementById('newJobBtn'),

  // Error elements
  errorMessage: document.getElementById('errorMessage'),
  retryBtn: document.getElementById('retryBtn')
};

// State
let currentJobId = null;
let statusCheckInterval = null;
let currentProgress = 0;
let targetProgress = 0;

/**
 * Initialize popup
 */
async function init() {
  // Load resumes
  await loadResumes();

  // Check for in-progress job
  const storage = await chrome.storage.local.get(['currentJobId', 'cancelled']);
  if (storage.currentJobId && !storage.cancelled) {
    currentJobId = storage.currentJobId;
    showView('processingView');
    startPolling();
  }

  // Check current tab for auto-scraping
  await checkForAutoScrape();

  // Load saved preferences
  await loadPreferences();

  // Setup event listeners
  setupEventListeners();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Pop-out button
  const popOutBtn = document.getElementById('popOutBtn');
  if (popOutBtn) {
    popOutBtn.addEventListener('click', () => {
      chrome.tabs.create({
        url: chrome.runtime.getURL('popup/popup.html')
      });
    });
  }

  // Character count
  elements.jobPosting.addEventListener('input', updateCharCount);

  // Form validation
  elements.jobPosting.addEventListener('input', validateForm);
  elements.resumeSelect.addEventListener('change', validateForm);

  // Submit button
  elements.submitBtn.addEventListener('click', handleSubmit);

  // Cancel button
  elements.cancelBtn.addEventListener('click', handleCancel);

  // New job button
  elements.newJobBtn.addEventListener('click', () => {
    resetForm();
    showView('formView');
  });

  // Retry button
  elements.retryBtn.addEventListener('click', () => {
    resetForm();
    showView('formView');
  });

  // Save preferences on change
  elements.includeExperience.addEventListener('change', savePreferences);
  elements.renderPdf.addEventListener('change', savePreferences);
  elements.resumeSelect.addEventListener('change', savePreferences);
}

/**
 * Load resumes from backend
 */
async function loadResumes() {
  try {
    const response = await sendMessage({ type: 'GET_RESUMES' });

    if (!response.success) {
      throw new Error(response.error);
    }

    const resumes = response.resumes;
    elements.resumeSelect.innerHTML = '';

    if (resumes.length === 0) {
      elements.resumeSelect.innerHTML = '<option value="">No resumes available</option>';
      elements.submitBtn.disabled = true;
      return;
    }

    resumes.forEach(resume => {
      const option = document.createElement('option');
      option.value = resume.id;
      option.textContent = resume.name || resume.id;
      elements.resumeSelect.appendChild(option);
    });

    validateForm();
  } catch (error) {
    console.error('Failed to load resumes:', error);
    elements.resumeSelect.innerHTML = '<option value="">Failed to load resumes</option>';
    showError('Could not connect to backend. Make sure the server is running at http://localhost:8000');
  }
}

/**
 * Check if current tab has a job posting we can scrape
 */
async function checkForAutoScrape() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.url) return;

    const url = tab.url;
    const isLinkedIn = url.includes('linkedin.com/jobs');
    const isIndeed = url.includes('indeed.com/viewjob');

    if (!isLinkedIn && !isIndeed) return;

    // Request scraped content from content script
    chrome.tabs.sendMessage(tab.id, { type: 'GET_JOB_DESCRIPTION' }, response => {
      if (chrome.runtime.lastError) {
        console.log('Content script not ready:', chrome.runtime.lastError.message);
        return;
      }

      if (response && response.jobDescription) {
        elements.jobPosting.value = response.jobDescription;
        updateCharCount();
        validateForm();
        showScrapedNotice();
      }
    });
  } catch (error) {
    console.log('Auto-scrape check failed:', error);
  }
}

/**
 * Show scraped notice
 */
function showScrapedNotice() {
  elements.scrapedNotice.classList.remove('hidden');
  setTimeout(() => {
    elements.scrapedNotice.classList.add('hidden');
  }, 5000);
}

/**
 * Update character count
 */
function updateCharCount() {
  const length = elements.jobPosting.value.length;
  elements.charCount.textContent = `${length} characters (min 50)`;
}

/**
 * Validate form
 */
function validateForm() {
  const jobPostingValid = elements.jobPosting.value.trim().length >= 50;
  const resumeValid = elements.resumeSelect.value !== '';

  elements.submitBtn.disabled = !(jobPostingValid && resumeValid);
}

/**
 * Handle form submission
 */
async function handleSubmit() {
  const data = {
    job_posting: elements.jobPosting.value.trim(),
    original_resume_id: elements.resumeSelect.value,
    include_experience: elements.includeExperience.checked,
    render_pdf: elements.renderPdf.checked
  };

  try {
    showView('processingView');
    resetProgress();

    const response = await sendMessage({
      type: 'SUBMIT_TAILOR_JOB',
      data: data
    });

    if (!response.success) {
      throw new Error(response.error);
    }

    currentJobId = response.job_id;
    startPolling();

  } catch (error) {
    console.error('Submit error:', error);
    showError(error.message || 'Failed to submit job. Please try again.');
  }
}

/**
 * Handle cancel
 */
async function handleCancel() {
  stopPolling();
  await sendMessage({ type: 'CANCEL_JOB' });
  currentJobId = null;
  resetForm();
  showView('formView');
}

/**
 * Start polling job status
 */
function startPolling() {
  statusCheckInterval = setInterval(checkJobStatus, 2000);
  checkJobStatus(); // Check immediately
}

/**
 * Stop polling
 */
function stopPolling() {
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
    const response = await sendMessage({
      type: 'CHECK_JOB_STATUS',
      job_id: currentJobId
    });

    if (!response.success) {
      throw new Error(response.error);
    }

    const data = response.data;

    // Update progress with smooth animation
    updateProgress(data.progress || 0, data.message || 'Processing...');

    // Append logs
    if (data.logs) {
      appendLogs(data.logs);
    }

    // Handle status
    if (data.status === 'completed') {
      stopPolling();
      currentJobId = null;
      showResults(data.result);
    } else if (data.status === 'failed') {
      stopPolling();
      currentJobId = null;
      showError(data.error || 'Job failed. Please try again.');
    }

  } catch (error) {
    console.error('Status check error:', error);
    // Don't stop polling on network errors, just log
    if (error.message.includes('Job not found')) {
      stopPolling();
      currentJobId = null;
      showError(error.message);
    }
  }
}

/**
 * Update progress bar with smooth animation
 */
function updateProgress(progress, message) {
  targetProgress = progress;
  elements.progressText.textContent = message;

  // Smooth animation
  animateProgress();
}

/**
 * Animate progress bar smoothly
 */
function animateProgress() {
  if (currentProgress < targetProgress) {
    currentProgress += (targetProgress - currentProgress) * 0.1;

    if (targetProgress - currentProgress < 0.5) {
      currentProgress = targetProgress;
    }

    elements.progressBar.style.width = `${currentProgress}%`;
    elements.progressPercent.textContent = `${Math.round(currentProgress)}%`;

    if (currentProgress < targetProgress) {
      requestAnimationFrame(animateProgress);
    }
  }
}

/**
 * Append logs to terminal
 */
function appendLogs(logs) {
  if (!logs || logs.length === 0) return;

  const currentText = elements.terminalLogs.textContent;
  const newText = logs.join('\n');

  if (currentText) {
    elements.terminalLogs.textContent = currentText + '\n' + newText;
  } else {
    elements.terminalLogs.textContent = newText;
  }

  // Auto-scroll to bottom
  elements.terminalLogs.parentElement.scrollTop = elements.terminalLogs.parentElement.scrollHeight;
}

/**
 * Show results
 */
function showResults(result) {
  elements.resultCompany.textContent = result.company || '-';
  elements.resultPosition.textContent = result.position || '-';

  // Set download links
  const resultId = result.id || result.result_id;
  if (resultId) {
    elements.downloadTexBtn.href = `http://localhost:8000/api/results/${resultId}/tex`;
    elements.downloadPdfBtn.href = `http://localhost:8000/api/results/${resultId}/pdf`;
  }

  showView('resultsView');
}

/**
 * Show error
 */
function showError(message) {
  elements.errorMessage.textContent = message;
  showView('errorView');
}

/**
 * Show specific view
 */
function showView(viewName) {
  elements.formView.classList.add('hidden');
  elements.processingView.classList.add('hidden');
  elements.resultsView.classList.add('hidden');
  elements.errorView.classList.add('hidden');

  elements[viewName].classList.remove('hidden');
}

/**
 * Reset form
 */
function resetForm() {
  elements.jobPosting.value = '';
  updateCharCount();
  validateForm();
}

/**
 * Reset progress
 */
function resetProgress() {
  currentProgress = 0;
  targetProgress = 0;
  elements.progressBar.style.width = '0%';
  elements.progressPercent.textContent = '0%';
  elements.progressText.textContent = 'Starting...';
  elements.terminalLogs.textContent = '';
}

/**
 * Load saved preferences
 */
async function loadPreferences() {
  const storage = await chrome.storage.local.get(['lastResume', 'includeExperience', 'renderPdf']);

  if (storage.lastResume) {
    elements.resumeSelect.value = storage.lastResume;
  }

  if (storage.includeExperience !== undefined) {
    elements.includeExperience.checked = storage.includeExperience;
  }

  if (storage.renderPdf !== undefined) {
    elements.renderPdf.checked = storage.renderPdf;
  } else {
    elements.renderPdf.checked = true; // Default to true
  }

  validateForm();
}

/**
 * Save preferences
 */
async function savePreferences() {
  await chrome.storage.local.set({
    lastResume: elements.resumeSelect.value,
    includeExperience: elements.includeExperience.checked,
    renderPdf: elements.renderPdf.checked
  });
}

/**
 * Send message to service worker
 */
function sendMessage(message) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(message, response => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
      } else {
        resolve(response);
      }
    });
  });
}

// Initialize on load
init();
