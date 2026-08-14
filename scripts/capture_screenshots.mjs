import { mkdir } from "node:fs/promises";
import { chromium } from "playwright";

const baseUrl = process.env.BASE_URL ?? "http://127.0.0.1:8024";
const outputDir = new URL("../docs/screenshots/", import.meta.url);
const executablePath = process.env.CHROME_BIN ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  executablePath,
  headless: true,
  args: ["--disable-background-networking", "--disable-component-update", "--no-first-run"],
});
const shots = [
  ["01-command-center", "/#overview", 1500, 1100],
  ["02-classify-ticket", "/#classify", 1500, 1100],
  ["04-review-queue", "/#queue", 1500, 1100],
  ["05-model-observability", "/#observability", 1500, 1100],
  ["06-knowledge-assist", "/#knowledge", 1500, 1100],
  ["07-model-card", "/#model-card", 1500, 1100],
  ["08-system-design", "/#about", 1500, 1100],
  ["09-command-center-mobile", "/#overview", 430, 932],
  ["03-classification-result", "/?demo=result#classify", 1500, 1100, "#resultContent:not(.hidden)"],
  ["10-classifier-mobile", "/?demo=result#classify", 430, 932, "#resultContent:not(.hidden)"],
];

for (const [name, path, width, height, waitSelector] of shots) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.goto(`${baseUrl}${path}`, { waitUntil: "networkidle" });
  if (waitSelector) await page.locator(waitSelector).waitFor({ state: "visible", timeout: 15_000 });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: new URL(`${name}.png`, outputDir).pathname, fullPage: false });
  await page.close();
}

await browser.close();
console.log(`Captured ${shots.length} product screenshots`);
