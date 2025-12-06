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
  scrapeBtn: document.getElementById('scrapeBtn'),
  reloadScraperBtn: document.getElementById('reloadScraperBtn'),
  jobPosting: document.getElementById('jobPosting'),
  charCount: document.getElementById('charCount'),
  companyName: document.getElementById('companyName'),
  desiredTitle: document.getElementById('desiredTitle'),
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
let lastScrapedJobId = null;  // Track last scraped LinkedIn job ID for auto-scrape

/**
 * Extract LinkedIn currentJobId from URL
 */
function extractLinkedInJobId(url) {
  if (!url) return null;
  const match = url.match(/currentJobId=(\d+)/);
  return match ? match[1] : null;
}

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

  // Check if scraping is available on current page
  const scrapingAvailable = await checkScrapingAvailable();

  // If side panel opens on a job posting page, auto-scrape immediately
  if (scrapingAvailable) {
    console.log('Side panel opened on job posting page, auto-scraping...');
    await autoScrapeJob();
  }

  // Load saved preferences
  await loadPreferences();

  // Setup event listeners
  setupEventListeners();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Character count
  elements.jobPosting.addEventListener('input', updateCharCount);

  // Form validation
  elements.jobPosting.addEventListener('input', validateForm);
  elements.resumeSelect.addEventListener('change', validateForm);

  // Manual scrape button
  elements.scrapeBtn.addEventListener('click', handleScrapeClick);

  // Reload scraper button (force re-inject content script)
  elements.reloadScraperBtn.addEventListener('click', handleReloadScraper);

  // Submit button
  elements.submitBtn.addEventListener('click', handleSubmit);

  // Cancel button
  elements.cancelBtn.addEventListener('click', handleCancel);

  // New job button
  elements.newJobBtn.addEventListener('click', async () => {
    resetForm();
    showView('formView');
    await checkScrapingAvailable();
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

  // Listen for tab updates (when user navigates while side panel is open)
  chrome.tabs.onUpdated.addListener(async (_tabId, changeInfo, tab) => {
    // Only care about completed page loads on active tab
    if (changeInfo.status === 'complete' && tab.active && tab.url) {
      const scrapingAvailable = await checkScrapingAvailable();

      if (scrapingAvailable) {
        // Extract job ID from LinkedIn URL
        const jobId = extractLinkedInJobId(tab.url);

        // Auto-scrape if this is a new job (different from last scraped)
        if (jobId && jobId !== lastScrapedJobId) {
          console.log('New job detected:', jobId, '(last was:', lastScrapedJobId, ')');
          await autoScrapeJob();
        }
      }
    }
  });

  // Listen for tab activation (when user switches tabs while side panel is open)
  chrome.tabs.onActivated.addListener(async () => {
    await checkScrapingAvailable();
  });
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
 * Inject content script if not already present
 */
async function ensureContentScriptLoaded(tabId, url) {
  const isLinkedIn = url.includes('linkedin.com/jobs');
  const isIndeed = url.includes('indeed.com/viewjob');

  if (!isLinkedIn && !isIndeed) return false;

  try {
    // Try to ping the content script
    await chrome.tabs.sendMessage(tabId, { type: 'PING' });
    return true; // Already loaded
  } catch (error) {
    // Content script not loaded, inject it via service worker
    console.log('Content script not loaded, requesting injection...');

    try {
      const scriptFile = isLinkedIn ? 'content/linkedin-scraper.js' : 'content/indeed-scraper.js';

      // Ask service worker to inject the script (side panels can't use chrome.scripting directly)
      const response = await chrome.runtime.sendMessage({
        type: 'INJECT_CONTENT_SCRIPT',
        tabId: tabId,
        scriptFile: scriptFile
      });

      if (response.success) {
        console.log('Content script injected successfully');
        // Wait longer for script to initialize (LinkedIn is slow)
        await new Promise(resolve => setTimeout(resolve, 1500));
        return true;
      } else {
        console.error('Service worker failed to inject script:', response.error);
        return false;
      }
    } catch (injectError) {
      console.error('Failed to inject content script:', injectError);
      return false;
    }
  }
}

/**
 * Core scraping function (reusable for auto and manual scraping)
 * Returns { jobDescription: string } or null
 */
async function scrapeCurrentPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.url) return null;

    const url = tab.url;
    const isLinkedIn = url.includes('linkedin.com/jobs');
    const isIndeed = url.includes('indeed.com/viewjob');

    if (!isLinkedIn && !isIndeed) return null;

    // Ensure content script is loaded before trying to scrape
    const scriptLoaded = await ensureContentScriptLoaded(tab.id, url);
    if (!scriptLoaded) {
      console.log('Content script could not be loaded');
      return null;
    }

    return new Promise((resolve, reject) => {
      // Increased timeout to 20s to account for scraper's 15s wait + processing time
      const timeout = setTimeout(() => {
        console.error('Content script timeout after 20s');
        reject(new Error('Content script not responding'));
      }, 20000);

      console.log('Sending GET_JOB_DESCRIPTION message to tab:', tab.id);

      chrome.tabs.sendMessage(
        tab.id,
        { type: 'GET_JOB_DESCRIPTION' },
        response => {
          clearTimeout(timeout);

          if (chrome.runtime.lastError) {
            console.error('Chrome runtime error:', chrome.runtime.lastError.message);
            reject(new Error(chrome.runtime.lastError.message));
            return;
          }

          resolve(response);
        }
      );
    });
  } catch (error) {
    console.log('Scrape failed:', error);
    return null;
  }
}

/**
 * Check if scraping is available on current page and show/hide button
 */
async function checkScrapingAvailable() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.url) {
      elements.scrapeBtn.classList.add('hidden');
      return false;
    }

    const url = tab.url;

    // LinkedIn: Must have /jobs/ AND a job ID parameter (currentJobId=)
    const isLinkedInJob = url.includes('linkedin.com/jobs') && url.includes('currentJobId=');

    // Indeed: Must have /viewjob in the path
    const isIndeedJob = url.includes('indeed.com/viewjob');

    if (!isLinkedInJob && !isIndeedJob) {
      elements.scrapeBtn.classList.add('hidden');
      elements.reloadScraperBtn.classList.add('hidden');
      return false;
    }

    elements.scrapeBtn.classList.remove('hidden');
    elements.scrapeBtn.disabled = false;
    elements.reloadScraperBtn.classList.remove('hidden');
    elements.reloadScraperBtn.disabled = false;
    return true;
  } catch (error) {
    console.log('Scraping availability check failed:', error);
    elements.scrapeBtn.classList.add('hidden');
    elements.reloadScraperBtn.classList.add('hidden');
    return false;
  }
}

/**
 * Auto-scrape when navigating to a new job (with retry logic for slow LinkedIn)
 */
async function autoScrapeJob(isRetry = false) {
  try {
    console.log(isRetry ? 'Retrying auto-scrape...' : 'Auto-scraping job posting...');

    const response = await scrapeCurrentPage();

    if (response && response.jobDescription) {
      elements.jobPosting.value = response.jobDescription;

      // Populate company and title if scraped
      if (response.company) {
        elements.companyName.value = response.company;
      }
      if (response.title) {
        elements.desiredTitle.value = response.title;
      }

      // Track this job as scraped (for auto-scrape detection)
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab?.url) {
        lastScrapedJobId = extractLinkedInJobId(tab.url);
        console.log('Updated lastScrapedJobId:', lastScrapedJobId);
      }

      updateCharCount();
      validateForm();
      showScrapedNotice('New job detected - auto-filled', 'success');

      // Update scrape button text to indicate re-scrape
      elements.scrapeBtn.textContent = 'Re-scrape Job Posting';
    } else {
      console.log('Auto-scrape found no content');
      // Retry once after 3 seconds if this was the first attempt
      if (!isRetry) {
        console.log('Will retry auto-scrape in 3 seconds...');
        setTimeout(() => autoScrapeJob(true), 3000);
      }
    }
  } catch (error) {
    console.error('Auto-scrape error:', error);
    // Retry once on error if this was the first attempt
    if (!isRetry) {
      console.log('Will retry auto-scrape in 3 seconds...');
      setTimeout(() => autoScrapeJob(true), 3000);
    }
  }
}

/**
 * Handle manual scrape button click
 */
async function handleScrapeClick() {
  if (elements.scrapeBtn.disabled) return;

  const previousContent = elements.jobPosting.value;

  try {
    elements.scrapeBtn.disabled = true;
    elements.scrapeBtn.textContent = 'Scraping...';

    const response = await scrapeCurrentPage();

    if (response && response.jobDescription) {
      elements.jobPosting.value = response.jobDescription;

      // Populate company and title if scraped
      if (response.company) {
        elements.companyName.value = response.company;
      }
      if (response.title) {
        elements.desiredTitle.value = response.title;
      }

      updateCharCount();
      validateForm();
      showScrapedNotice('Job posting updated - page re-scraped', 'success');
    } else {
      elements.jobPosting.value = previousContent;
      showScrapedNotice('No job posting found on this page', 'error');
    }
  } catch (error) {
    console.error('Manual scrape error:', error);
    elements.jobPosting.value = previousContent;
    showScrapedNotice(error.message || 'Failed to scrape job posting', 'error');
  } finally {
    elements.scrapeBtn.textContent = 'Re-scrape Job Posting';
    elements.scrapeBtn.disabled = false;
  }
}

/**
 * Handle reload scraper button - force re-inject content script and scrape
 */
async function handleReloadScraper() {
  if (elements.reloadScraperBtn.disabled) return;

  try {
    elements.reloadScraperBtn.disabled = true;
    elements.reloadScraperBtn.textContent = '↻ Reloading...';
    elements.scrapeBtn.disabled = true;

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      showScrapedNotice('No active tab found', 'error');
      return;
    }

    const url = tab.url;
    const isLinkedIn = url.includes('linkedin.com/jobs');
    const isIndeed = url.includes('indeed.com/viewjob');
    const scriptFile = isLinkedIn ? 'content/linkedin-scraper.js' : 'content/indeed-scraper.js';

    console.log('Force re-injecting content script...');

    // Force inject content script (will create new listener)
    const response = await chrome.runtime.sendMessage({
      type: 'INJECT_CONTENT_SCRIPT',
      tabId: tab.id,
      scriptFile: scriptFile
    });

    if (!response.success) {
      throw new Error('Failed to inject content script');
    }

    console.log('Content script re-injected, waiting for initialization...');
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Now try to scrape
    elements.reloadScraperBtn.textContent = '↻ Scraping...';
    const scrapeResponse = await scrapeCurrentPage();

    if (scrapeResponse && scrapeResponse.jobDescription) {
      elements.jobPosting.value = scrapeResponse.jobDescription;

      if (scrapeResponse.company) {
        elements.companyName.value = scrapeResponse.company;
      }
      if (scrapeResponse.title) {
        elements.desiredTitle.value = scrapeResponse.title;
      }

      updateCharCount();
      validateForm();
      showScrapedNotice('Scraper reloaded - job posting found!', 'success');
    } else {
      showScrapedNotice('Scraper reloaded but no content found', 'error');
    }
  } catch (error) {
    console.error('Reload scraper error:', error);
    showScrapedNotice('Reload failed: ' + error.message, 'error');
  } finally {
    elements.reloadScraperBtn.textContent = '↻ Reload';
    elements.reloadScraperBtn.disabled = false;
    elements.scrapeBtn.disabled = false;
  }
}

/**
 * Show notification for scrape result (auto-scrape or manual)
 * @param {string} message - Notification message
 * @param {string} type - 'success' or 'error'
 */
function showScrapedNotice(message = 'Job posting detected and auto-filled', type = 'success') {
  const classes = ['brutalist-chip'];

  if (type === 'success') {
    classes.push('brutalist-chip--success');
  } else if (type === 'error') {
    classes.push('brutalist-chip--error');
  }

  elements.scrapedNotice.className = classes.join(' ');
  elements.scrapedNotice.textContent = message;
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

  // Add optional fields only if provided (like SPA does)
  const companyName = elements.companyName.value.trim();
  const desiredTitle = elements.desiredTitle.value.trim();

  if (companyName) {
    data.company_name = companyName;
  }
  if (desiredTitle) {
    data.desired_title = desiredTitle;
  }

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

  // Convert logs to strings (in case they're objects)
  const logStrings = logs.map(log => {
    if (typeof log === 'string') return log;
    if (typeof log === 'object' && log !== null) {
      // If it's an object, try to get a meaningful string
      return log.message || log.text || JSON.stringify(log);
    }
    return String(log);
  });

  const currentText = elements.terminalLogs.textContent;
  const newText = logStrings.join('\n');

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
  console.log('showResults called with:', result);

  elements.resultCompany.textContent = result.company || '-';
  elements.resultPosition.textContent = result.position || '-';

  // Get file paths from result (backend returns full system paths)
  if (!result.tex_path) {
    console.error('No tex_path found in result object');
    return;
  }

  // Extract filename from path and get result_id (filename without extension)
  const texFilename = result.tex_path.split('\\').pop().split('/').pop();
  const resultId = texFilename.replace('.tex', '');

  // Use the correct API endpoints
  const texUrl = `http://localhost:8000/api/results/${resultId}/tex`;
  const pdfUrl = result.pdf_path ? `http://localhost:8000/api/results/${resultId}/pdf` : null;

  console.log('Download URLs:', { texUrl, pdfUrl });
  console.log('Result ID:', resultId);

  // Set download attributes for .tex
  elements.downloadTexBtn.setAttribute('href', texUrl);
  elements.downloadTexBtn.setAttribute('download', `${resultId}.tex`);
  elements.downloadTexBtn.setAttribute('target', '_blank');

  // Set download attributes for .pdf if available
  if (pdfUrl) {
    elements.downloadPdfBtn.setAttribute('href', pdfUrl);
    elements.downloadPdfBtn.setAttribute('download', `${resultId}.pdf`);
    elements.downloadPdfBtn.setAttribute('target', '_blank');
    elements.downloadPdfBtn.style.display = '';
  } else {
    elements.downloadPdfBtn.style.display = 'none';
  }

  console.log('Download buttons configured successfully');

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
  elements.companyName.value = '';
  elements.desiredTitle.value = '';
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
