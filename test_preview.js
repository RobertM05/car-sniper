const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
  page.on('pageerror', error => console.log('BROWSER ERROR:', error.message));
  await page.goto('https://motorbit-6e6x6x024-robertm05s-projects.vercel.app/');
  await page.waitForTimeout(3000);
  await browser.close();
})();
