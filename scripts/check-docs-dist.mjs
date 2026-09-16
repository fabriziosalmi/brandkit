import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const distDir = path.join(rootDir, 'docs', '.vitepress', 'dist');

if (!fs.existsSync(distDir)) {
  console.error(`Error: Dist directory does not exist at ${distDir}. Run docs build first.`);
  process.exit(1);
}

const requiredNonEmptyFiles = [
  'sitemap.xml',
  'robots.txt',
  'llms.txt',
  'llms-full.txt',
  path.join('.well-known', 'security.txt'),
  'favicon.svg',
  'og-image.png'
];

for (const relPath of requiredNonEmptyFiles) {
  const fullPath = path.join(distDir, relPath);
  if (!fs.existsSync(fullPath)) {
    console.error(`missing: ${relPath}`);
    process.exit(1);
  }
  const stats = fs.statSync(fullPath);
  if (stats.size === 0) {
    console.error(`empty: ${relPath}`);
    process.exit(1);
  }
}

const nojekyllPath = path.join(distDir, '.nojekyll');
if (!fs.existsSync(nojekyllPath)) {
  console.error('missing: .nojekyll');
  process.exit(1);
}

const indexPath = path.join(distDir, 'index.html');
if (!fs.existsSync(indexPath)) {
  console.error('missing: index.html');
  process.exit(1);
}

const indexContent = fs.readFileSync(indexPath, 'utf-8');
if (!indexContent.includes('application/ld+json')) {
  console.error('missing: schema.org JSON-LD');
  process.exit(1);
}

console.log('all artefacts present');
