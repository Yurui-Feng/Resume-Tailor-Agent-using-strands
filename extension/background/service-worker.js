/**
 * Service Worker for Resume Tailor Extension
 * Handles all API communication with the backend
 */

const API_BASE = 'http://localhost:8000/api';

/**
 * Message handler - receives messages from popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_RESUMES') {
    getResumes()
      .then(resumes => sendResponse({ success: true, resumes }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }

  if (message.type === 'SUBMIT_TAILOR_JOB') {
    submitTailorJob(message.data)
      .then(response => sendResponse({ success: true, job_id: response.job_id }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }

  if (message.type === 'CHECK_JOB_STATUS') {
    checkJobStatus(message.job_id)
      .then(data => sendResponse({ success: true, data }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }

  if (message.type === 'CANCEL_JOB') {
    // Store cancellation flag
    chrome.storage.local.set({ cancelled: true });
    sendResponse({ success: true });
    return true;
  }

  if (message.type === 'INJECT_CONTENT_SCRIPT') {
    injectContentScript(message.tabId, message.scriptFile)
      .then(() => sendResponse({ success: true }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

/**
 * Get list of available resumes
 */
async function getResumes() {
  try {
    const response = await fetch(`${API_BASE}/resumes`);

    if (!response.ok) {
      throw new Error(`Failed to load resumes: ${response.status}`);
    }

    const resumes = await response.json();
    return resumes;
  } catch (error) {
    console.error('Error fetching resumes:', error);
    throw new Error('Could not connect to backend. Is the server running?');
  }
}

/**
 * Submit a resume tailoring job
 */
async function submitTailorJob(data) {
  try {
    const response = await fetch(`${API_BASE}/tailor`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to submit job: ${response.status}`);
    }

    const result = await response.json();

    // Store current job ID for recovery
    await chrome.storage.local.set({
      currentJobId: result.job_id,
      cancelled: false
    });

    return result;
  } catch (error) {
    console.error('Error submitting job:', error);
    throw error;
  }
}

/**
 * Check job status
 */
async function checkJobStatus(jobId) {
  try {
    const response = await fetch(`${API_BASE}/jobs/${jobId}/status`);

    if (response.status === 404) {
      throw new Error('Job not found. It may have expired.');
    }

    if (!response.ok) {
      throw new Error(`Failed to check status: ${response.status}`);
    }

    const data = await response.json();

    // If job completed or failed, clear storage
    if (data.status === 'completed' || data.status === 'failed') {
      await chrome.storage.local.remove(['currentJobId', 'cancelled']);
    }

    return data;
  } catch (error) {
    console.error('Error checking job status:', error);
    throw error;
  }
}

/**
 * Inject content script programmatically
 */
async function injectContentScript(tabId, scriptFile) {
  try {
    if (!chrome.scripting) {
      throw new Error('chrome.scripting API is not available');
    }

    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      files: [scriptFile]
    });
    console.log('Content script injected:', scriptFile);
  } catch (error) {
    console.error('Failed to inject content script:', error);
    console.error('Tab ID:', tabId, 'Script file:', scriptFile);
    throw error;
  }
}

/**
 * Installation handler
 */
chrome.runtime.onInstalled.addListener(() => {
  console.log('Resume Tailor Extension installed');
});

/**
 * Handle extension icon click - open side panel
 */
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ windowId: tab.windowId });
});
