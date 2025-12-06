/**
 * LinkedIn Job Scraper Content Script
 * Extracts job description from LinkedIn job posting pages
 *
 * NOTE: This script runs in the ISOLATED world by default, but LinkedIn's
 * dynamic content may not be visible there. We inject a script into the
 * MAIN world to access the actual DOM.
 */

/**
 * Scrape job data by injecting into the main world
 * This bypasses the isolated world limitation where dynamic content isn't visible
 */
function scrapeViaMainWorld() {
  return new Promise((resolve) => {
    // Create a unique callback name
    const callbackId = 'linkedinScrapeCallback_' + Date.now();

    // Listen for the result
    window.addEventListener(callbackId, function handler(event) {
      window.removeEventListener(callbackId, handler);
      resolve(event.detail);
    });

    // Inject script into the page's main world
    const script = document.createElement('script');
    script.textContent = `
      (function() {
        const selectors = [
          '#job-details',
          '.jobs-description__container',
          '.show-more-less-html__markup',
          '.jobs-description__content',
          '.jobs-box__html-content',
          '.jobs-description-content__text'
        ];

        let description = null;
        let descEl = null;

        for (const sel of selectors) {
          descEl = document.querySelector(sel);
          if (descEl) {
            description = descEl.innerText.trim();
            break;
          }
        }

        // Get title
        const titleSelectors = [
          '.top-card-layout__title',
          '.jobs-unified-top-card__job-title',
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
          '.topcard__org-name-link',
          '.jobs-unified-top-card__company-name',
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

        // Dispatch result back to content script
        window.dispatchEvent(new CustomEvent('${callbackId}', {
          detail: { description, title, company }
        }));
      })();
    `;

    document.documentElement.appendChild(script);
    script.remove();

    // Timeout fallback
    setTimeout(() => resolve(null), 5000);
  });
}

/**
 * Wait for element to appear in DOM using polling (more reliable for SPAs)
 */
function waitForElement(selector, timeout = 15000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const element = document.querySelector(selector);
      if (element) {
        console.log('Found element:', selector);
        resolve(element);
        return;
      }

      if (Date.now() - startTime > timeout) {
        reject(new Error(`Element ${selector} not found within timeout`));
        return;
      }

      // Poll every 500ms
      setTimeout(check, 500);
    };

    check();
  });
}

/**
 * Scrape LinkedIn job posting
 * Uses main world injection to bypass isolated world DOM limitations
 */
async function scrapeLinkedInJob() {
  try {
    console.log('LinkedIn scraper: Starting scrape via main world injection...');
    console.log('Current URL:', window.location.href);

    // Try the main world injection approach first (most reliable)
    const mainWorldResult = await scrapeViaMainWorld();

    if (mainWorldResult && mainWorldResult.description) {
      console.log('LinkedIn scraper: Found job via main world injection');

      // Build full description with title and company
      let fullDescription = '';
      if (mainWorldResult.title && mainWorldResult.company) {
        fullDescription = `${mainWorldResult.title} at ${mainWorldResult.company}\n\n`;
      }
      fullDescription += mainWorldResult.description;

      return {
        jobDescription: fullDescription,
        company: mainWorldResult.company,
        title: mainWorldResult.title
      };
    }

    console.log('LinkedIn scraper: Main world injection found no content, trying isolated world...');

    // Fallback: try isolated world (in case CSP blocks script injection)
    const descriptionSelectors = [
      '#job-details',
      '.jobs-description__container',
      '.show-more-less-html__markup',
      '.jobs-description__content',
      '.jobs-box__html-content',
      '.jobs-description-content__text'
    ];

    let descriptionElement = null;
    for (const selector of descriptionSelectors) {
      descriptionElement = document.querySelector(selector);
      if (descriptionElement) {
        console.log('Found in isolated world with:', selector);
        break;
      }
    }

    if (!descriptionElement) {
      // Wait a bit for dynamic content
      console.log('Waiting for content in isolated world...');
      await new Promise(resolve => setTimeout(resolve, 2000));

      for (const selector of descriptionSelectors) {
        descriptionElement = document.querySelector(selector);
        if (descriptionElement) break;
      }
    }

    if (!descriptionElement) {
      console.error('LinkedIn scraper: No job description found in either world');
      return null;
    }

    const description = descriptionElement.innerText.trim();

    // Get title
    let title = null;
    const titleEl = document.querySelector('.jobs-unified-top-card__job-title') ||
                    document.querySelector('h1');
    if (titleEl) title = titleEl.innerText.trim();

    // Get company
    let company = null;
    const companyEl = document.querySelector('.jobs-unified-top-card__company-name') ||
                      document.querySelector('a[href*="/company/"]');
    if (companyEl) company = companyEl.innerText.trim();

    let fullDescription = '';
    if (title && company) {
      fullDescription = `${title} at ${company}\n\n`;
    }
    fullDescription += description;

    return {
      jobDescription: fullDescription,
      company: company,
      title: title
    };

  } catch (error) {
    console.error('LinkedIn scraper error:', error);
    return null;
  }
}

/**
 * Listen for messages from popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_JOB_DESCRIPTION') {
    scrapeLinkedInJob().then(result => {
      sendResponse(result);  // Now returns object with jobDescription, company, title
    });
    return true; // Keep channel open for async response
  }

  if (message.type === 'PING') {
    sendResponse({ status: 'ok' });
    return true;
  }
});

console.log('LinkedIn scraper content script loaded');
