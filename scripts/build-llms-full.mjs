// Concatenates every documentation page into docs/public/llms-full.txt so that
// an LLM can ingest the whole manual in one request. Run before `vitepress build`.
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const docs = resolve(root, 'docs')

// Explicit order: this is a manual, not a directory listing.
const PAGES = [
  'guide/index.md',
  'guide/getting-started.md',
  'guide/docker.md',
  'guide/usage.md',
  'guide/formats.md',
  'guide/preprocessing.md',
  'guide/background-removal.md',
  'guide/keyboard-shortcuts.md',
  'guide/deployment.md',
  'guide/performance.md',
  'guide/troubleshooting.md',
  'reference/configuration.md',
  'reference/environment.md',
  'reference/http-api.md',
  'reference/format-catalogue.md',
  'reference/changelog.md',
  'security.md',
  'privacy.md',
  'contributing.md',
  'code-of-conduct.md'
]

const SITE = 'https://fabriziosalmi.github.io/brandkit/'

const header = `# BrandKit — complete documentation

> Self-hosted brand asset generator. One source image in, 45 correctly-sized
> formats out, as PNG/JPG/WebP/ICO, with local AI background removal.
> Repository: https://github.com/fabriziosalmi/brandkit — MIT licensed.

This file is the full text of every page on ${SITE}, concatenated for machine
consumption. A short index is at ${SITE}llms.txt.

Generated: ${new Date().toISOString().slice(0, 10)}

---
`

// Strip YAML frontmatter, unwrap VitePress containers into plain markdown,
// and rewrite root-relative links to absolute ones.
function toPlainMarkdown(src, slug) {
  let body = src.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '')

  const LABELS = {
    tip: 'TIP', info: 'NOTE', warning: 'WARNING',
    danger: 'IMPORTANT', details: 'DETAILS'
  }

  // ::: type [title] ... :::  ->  **LABEL:** ...
  body = body.replace(
    /^:::\s*(tip|info|warning|danger|details)([^\n]*)\n([\s\S]*?)^:::\s*$/gm,
    (_m, type, title, inner) =>
      `> **${LABELS[type]}${title.trim() ? ` — ${title.trim()}` : ''}**\n` +
      inner.trimEnd().split('\n').map((l) => `> ${l}`).join('\n') + '\n'
  )

  // Drop raw HTML wrappers and <kbd>, keep their text.
  body = body.replace(/<\/?(?:div|span)[^>]*>/g, '')
  body = body.replace(/<kbd>(.*?)<\/kbd>/g, '`$1`')

  // /guide/docker -> absolute; leave external and anchor-only links alone.
  body = body.replace(/\]\(\/([^)\s]*)\)/g, (_m, path) => `](${SITE}${path})`)

  return `\n\n<!-- source: docs/${slug} -->\n\n${body.trim()}\n\n---\n`
}

let out = header
let missing = 0

for (const slug of PAGES) {
  const file = resolve(docs, slug)
  if (!existsSync(file)) {
    console.error(`build-llms-full: missing ${slug}`)
    missing++
    continue
  }
  out += toPlainMarkdown(readFileSync(file, 'utf8'), slug)
}

if (missing) {
  console.error(`build-llms-full: ${missing} page(s) missing — aborting`)
  process.exit(1)
}

const target = resolve(docs, 'public/llms-full.txt')
writeFileSync(target, out, 'utf8')
console.log(
  `build-llms-full: wrote ${target} (${PAGES.length} pages, ` +
  `${(out.length / 1024).toFixed(1)} KB)`
)
