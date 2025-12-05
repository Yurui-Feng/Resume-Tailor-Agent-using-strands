/**
 * Indeed Job Scraper Content Script
 * Extracts job description from Indeed job posting pages
 */

/**
 * Wait for element to appear in DOM (for SPAs)
 */
function waitForElement(selector, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const element = document.querySelector(selector);
      if (element) {
        resolve(element);
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('Element not found within timeout'));
      } else {
        setTimeout(check, 100);
      }
    };

    check();
  });
}

/**
 * Scrape Indeed job posting
 */
async function scrapeIndeedJob() {
  try {
    // Indeed job description container
    const descriptionSelectors = [
      '#jobDescriptionText',
      '.jobsearch-jobDescriptionText',
      '[class*="jobDescription"]'
    ];

    let descriptionElement = null;

    // Try each selector
    for (const selector of descriptionSelectors) {
      descriptionElement = document.querySelector(selector);
      if (descriptionElement) break;
    }

    // If not found, wait for SPA to load
    if (!descriptionElement) {
      descriptionElement = await waitForElement(descriptionSelectors[0], 3000).catch(() => null);
    }

    if (!descriptionElement) {
      console.log('Indeed job description not found');
      return null;
    }

    // Extract text content
    let description = descriptionElement.innerText.trim();

    // Try to get job title
    const titleSelectors = [
      '.jobsearch-JobInfoHeader-title',
      'h1[class*="jobTitle"]',
      '.jobsearch-JobInfoHeader-title-container'
    ];

    let titleElement = null;
    for (const selector of titleSelectors) {
      titleElement = document.querySelector(selector);
      if (titleElement) break;
    }

    // Try to get company name
    const companySelectors = [
      '[data-company-name="true"]',
      '.jobsearch-InlineCompanyRating',
      '[class*="companyName"]'
    ];

    let companyElement = null;
    for (const selector of companySelectors) {
      companyElement = document.querySelector(selector);
      if (companyElement) break;
    }

    // Extract title and company separately
    const title = titleElement ? titleElement.innerText.trim() : null;
    const company = companyElement ? companyElement.innerText.trim() : null;

    // Build full description with title and company
    let fullDescription = '';

    if (title && company) {
      fullDescription = `${title} at ${company}\n\n`;
    }

    fullDescription += description;

    // Return structured data instead of just string
    return {
      jobDescription: fullDescription,
      company: company,
      title: title
    };

  } catch (error) {
    console.error('Indeed scraper error:', error);
    return null;
  }
}

/**
 * Listen for messages from popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_JOB_DESCRIPTION') {
    scrapeIndeedJob().then(result => {
      sendResponse(result);  // Now returns object with jobDescription, company, title
    });
    return true; // Keep channel open for async response
  }

  if (message.type === 'PING') {
    sendResponse({ status: 'ok' });
    return true;
  }
});

console.log('Indeed scraper content script loaded');
