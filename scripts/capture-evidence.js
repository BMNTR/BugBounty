const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error("Usage: node capture-evidence.js <url> <outputDir>");
        process.exit(1);
    }

    const url = args[0];
    const outputDir = args[1];

    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const imagePath = path.join(outputDir, `evidence_${timestamp}.png`);
    const textPath = path.join(outputDir, `evidence_${timestamp}.txt`);

    let logText = `--- Evidence Capture Log ---\nURL: ${url}\nTimestamp: ${timestamp}\n\n`;

    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    const page = await context.newPage();

    // 1. Intercept Javascript Alerts/Prompts (The XSS Catcher)
    page.on('dialog', async dialog => {
        const msg = `[!] XSS Triggered! Dialog type: ${dialog.type()}, Message: ${dialog.message()}\n`;
        console.log(msg);
        logText += msg;
        await dialog.dismiss(); // Dismiss so the page can continue loading
    });

    // 2. Intercept Console Logs
    page.on('console', msg => {
        logText += `[Console ${msg.type()}] ${msg.text()}\n`;
    });

    // 3. Intercept Page Errors
    page.on('pageerror', error => {
        logText += `[Page Error] ${error.message}\n`;
    });

    try {
        console.log(`[+] Navigating to ${url}...`);
        // 4. Wait for network to be completely idle (no more loading screens)
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
        
        console.log(`[+] Taking perfect screenshot...`);
        // Add a small 2-second delay so the user can visually see what the bot is looking at
        await page.waitForTimeout(2000);
        await page.screenshot({ path: imagePath, fullPage: true });

        console.log(`[+] Extracting DOM HTML...`);
        const html = await page.content();
        logText += `\n--- HTML DOM Extraction ---\n`;
        logText += html;

        // Write the text evidence (Logs + HTML) to disk for Opencode to read
        fs.writeFileSync(textPath, logText);
        
        console.log(`[+] Success!`);
        console.log(`    Screenshot saved to: ${imagePath}`);
        console.log(`    Text Evidence saved to: ${textPath}`);

    } catch (error) {
        console.error(`[-] Error capturing evidence: ${error.message}`);
        logText += `\n[Fatal Error] ${error.message}\n`;
        fs.writeFileSync(textPath, logText);
    } finally {
        await browser.close();
    }
})();
