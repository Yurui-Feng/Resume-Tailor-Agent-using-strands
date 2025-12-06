/**
 * Service Worker for Resume Tailor Extension
 * Handles all API communication with the backend
 */

// Change this to your Mac Mini's IP when deploying remotely
// Local: 'http://localhost:8000/api'
// Mac Mini: 'http://10.10.10.2:8000/api'
const API_BASE = 'http://10.10.10.2:8000/api';

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

  if (message.type === 'SCRAPE_JOB_MAIN_WORLD') {
    scrapeJobInMainWorld(message.tabId)
      .then(result => sendResponse({ success: true, data: result }))
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
 * Scrape job posting by executing in the MAIN world
 * This bypasses the isolated world limitation where LinkedIn's dynamic content isn't visible
 */
async function scrapeJobInMainWorld(tabId) {
  try {
    console.log('Scraping job in MAIN world for tab:', tabId);

    const results = await chrome.scripting.executeScript({
      target: { tabId: tabId },
      world: 'MAIN',  // Run in page's main world, not isolated
      func: async () => {
        // Helper to poll for element with content
        const pollForElement = async (selectors, maxAttempts = 30, interval = 300) => {
          for (let attempt = 0; attempt < maxAttempts; attempt++) {
            for (const selector of selectors) {
              const el = document.querySelector(selector);
              if (el && el.innerText && el.innerText.trim().length > 50) {
                console.log(`[MAIN WORLD v4] Found element on attempt ${attempt + 1}:`, selector);
                return { element: el, selector };
              }
            }
            if (attempt < maxAttempts - 1) {
              await new Promise(r => setTimeout(r, interval));
            }
          }
          return null;
        };

        console.log('[MAIN WORLD v4] Starting scrape...');
        console.log('[MAIN WORLD v4] URL:', window.location.href);

        // Extract currentJobId from URL
        const urlMatch = window.location.href.match(/currentJobId=(\d+)/);
        const currentJobId = urlMatch ? urlMatch[1] : null;
        console.log('[MAIN WORLD v4] Target job ID:', currentJobId);

        // Quick check if page has job elements (popup.js handles reload if needed)
        const hasJobElements = document.querySelector('#job-details, [class*="jobs-description"], .jobs-search__job-details');
        console.log('[MAIN WORLD v4] Has job elements:', !!hasJobElements);

        const descriptionSelectors = [
          '#job-details',
          '.jobs-description__container',
          '.show-more-less-html__markup',
          '.jobs-description__content',
          '.jobs-box__html-content',
          '.jobs-description-content__text'
        ];

        // First quick check - maybe content is already there
        let result = null;
        for (const selector of descriptionSelectors) {
          const el = document.querySelector(selector);
          if (el && el.innerText && el.innerText.trim().length > 50) {
            console.log('[MAIN WORLD v4] Content already present:', selector);
            result = { element: el, selector };
            break;
          }
        }

        // If no content, try to trigger LinkedIn to load it
        if (!result && currentJobId) {
          console.log('[MAIN WORLD v4] No content yet, trying to trigger load...');

          // Find and click the job card in the list that matches our job ID
          // This forces LinkedIn's React to render the job details
          const jobCards = document.querySelectorAll('[data-job-id], .jobs-search-results__list-item, .job-card-container');
          console.log('[MAIN WORLD v4] Found job cards:', jobCards.length);

          let clickedCard = false;
          for (const card of jobCards) {
            // Check if this card's link contains our job ID
            const link = card.querySelector('a[href*="' + currentJobId + '"]') ||
                        (card.getAttribute('data-job-id') === currentJobId ? card : null);
            if (link || card.innerHTML.includes(currentJobId)) {
              console.log('[MAIN WORLD v4] Found matching job card, clicking...');
              // Find clickable element
              const clickTarget = card.querySelector('a') || card;
              clickTarget.click();
              clickedCard = true;
              await new Promise(r => setTimeout(r, 1000));
              break;
            }
          }

          // If we couldn't find a card to click, try scrolling to trigger lazy load
          if (!clickedCard) {
            console.log('[MAIN WORLD v4] No matching card found, trying scroll trigger...');
            const detailPane = document.querySelector('.jobs-search__job-details, .scaffold-layout__detail, .job-view-layout');
            if (detailPane) {
              detailPane.scrollIntoView({ behavior: 'instant' });
              // Also try scrolling within the pane
              detailPane.scrollTop = 100;
              await new Promise(r => setTimeout(r, 500));
              detailPane.scrollTop = 0;
            }
          }
        }

        // Now poll for the content
        if (!result) {
          result = await pollForElement(descriptionSelectors, 30, 300);
        }

        let description = null;
        if (result) {
          description = result.element.innerText.trim();
          console.log('[MAIN WORLD v4] Found description, length:', description.length);
        } else {
          console.log('[MAIN WORLD v4] No description found after polling');
        }

        // Get title
        const titleSelectors = [
          '.job-details-jobs-unified-top-card__job-title',
          '.jobs-unified-top-card__job-title',
          '.top-card-layout__title',
          'h1[class*="job-title"]',
          'h1'
        ];
        let title = null;
        for (const sel of titleSelectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText.trim()) {
            title = el.innerText.trim();
            break;
          }
        }

        // Get company
        const companySelectors = [
          '.job-details-jobs-unified-top-card__company-name',
          '.jobs-unified-top-card__company-name',
          '.topcard__org-name-link',
          'a[class*="company-name"]'
        ];
        let company = null;
        for (const sel of companySelectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText.trim()) {
            company = el.innerText.trim();
            break;
          }
        }

        console.log('[MAIN WORLD v4] Result:', { hasDescription: !!description, descLen: description?.length, title, company });
        return { description, title, company };
      }
    });

    if (results && results[0] && results[0].result) {
      const { description, title, company } = results[0].result;
      console.log('MAIN world scrape result:', { hasDescription: !!description, title, company });
      return { description, title, company };
    }

    return null;
  } catch (error) {
    console.error('MAIN world scrape error:', error);
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
