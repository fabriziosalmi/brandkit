import { defineConfig } from 'vitepress'
import taskLists from 'markdown-it-task-lists'

// Single source of truth for the deployed origin. Change these two if you move
// the site to a custom domain (and drop `base` to '/').
const HOSTNAME = 'https://fabriziosalmi.github.io'
const BASE = '/brandkit/'
const SITE_URL = HOSTNAME + BASE

const REPO = 'https://github.com/fabriziosalmi/brandkit'
const DESCRIPTION =
  'Self-hosted brand asset generator: upload one logo, get 45+ ready-to-ship ' +
  'sizes for web, social, mobile and print — with AI background removal, ' +
  'colour analysis and PNG/JPG/WebP/ICO output.'

const ldjson = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebSite',
      '@id': SITE_URL + '#website',
      url: SITE_URL,
      name: 'BrandKit',
      description: DESCRIPTION,
      inLanguage: 'en',
      publisher: { '@id': SITE_URL + '#person' }
    },
    {
      '@type': 'Person',
      '@id': SITE_URL + '#person',
      name: 'Fabrizio Salmi',
      url: 'https://github.com/fabriziosalmi'
    },
    {
      '@type': 'SoftwareApplication',
      '@id': SITE_URL + '#app',
      name: 'BrandKit',
      description: DESCRIPTION,
      url: SITE_URL,
      codeRepository: REPO,
      applicationCategory: 'DesignApplication',
      applicationSubCategory: 'Brand asset generator',
      operatingSystem: 'Linux, macOS, Windows (Docker)',
      softwareVersion: '1.1.3',
      programmingLanguage: ['Python', 'HTML'],
      runtimePlatform: 'Python 3.11+',
      license: 'https://opensource.org/licenses/MIT',
      author: { '@id': SITE_URL + '#person' },
      maintainer: { '@id': SITE_URL + '#person' },
      isAccessibleForFree: true,
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'USD'
      }
    },
    {
      '@type': 'TechArticle',
      '@id': SITE_URL + '#docs',
      headline: 'BrandKit documentation',
      description: DESCRIPTION,
      url: SITE_URL,
      about: { '@id': SITE_URL + '#app' },
      author: { '@id': SITE_URL + '#person' },
      inLanguage: 'en'
    }
  ]
}

export default defineConfig({
  lang: 'en-US',
  title: 'BrandKit',
  description: DESCRIPTION,
  base: BASE,
  cleanUrls: true,

  // Localhost URLs are instructions to the reader, not links to verify.
  ignoreDeadLinks: [/^https?:\/\/localhost/, /^https?:\/\/127\.0\.0\.1/],
  lastUpdated: true,
  metaChunk: true,

  markdown: {
    // Render `- [ ]` / `- [x]` as real (disabled) checkboxes — the deployment
    // and contributing pages lean on them.
    config: (md) => {
      md.use(taskLists, { enabled: false, label: true })
    }
  },

  sitemap: {
    hostname: SITE_URL,
    lastmodDateOnly: true
  },

  head: [
    ['link', { rel: 'icon', href: BASE + 'favicon.svg', type: 'image/svg+xml' }],
    ['meta', { name: 'theme-color', content: '#3b82f6' }],
    ['meta', { name: 'author', content: 'Fabrizio Salmi' }],
    ['meta', { name: 'robots', content: 'index, follow' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:site_name', content: 'BrandKit' }],
    ['meta', { property: 'og:title', content: 'BrandKit — self-hosted brand asset generator' }],
    ['meta', { property: 'og:description', content: DESCRIPTION }],
    ['meta', { property: 'og:url', content: SITE_URL }],
    ['meta', { property: 'og:image', content: SITE_URL + 'og-image.png' }],
    ['meta', { property: 'og:locale', content: 'en_US' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: 'BrandKit — self-hosted brand asset generator' }],
    ['meta', { name: 'twitter:description', content: DESCRIPTION }],
    ['meta', { name: 'twitter:image', content: SITE_URL + 'og-image.png' }],
    ['link', { rel: 'canonical', href: SITE_URL }],
    ['script', { type: 'application/ld+json' }, JSON.stringify(ldjson)]
  ],

  themeConfig: {
    logo: '/favicon.svg',
    siteTitle: 'BrandKit',

    nav: [
      { text: 'Guide', link: '/guide/', activeMatch: '/guide/' },
      { text: 'Reference', link: '/reference/configuration', activeMatch: '/reference/' },
      { text: 'Security', link: '/security', activeMatch: '/security' },
      {
        text: 'v1.1.3',
        items: [
          { text: 'Changelog', link: '/reference/changelog' },
          { text: 'Releases', link: REPO + '/releases' },
          { text: 'Contributing', link: '/contributing' },
          { text: 'License (MIT)', link: REPO + '/blob/main/LICENSE' }
        ]
      }
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Introduction',
          items: [
            { text: 'What is BrandKit?', link: '/guide/' },
            { text: 'Getting started', link: '/guide/getting-started' },
            { text: 'Running with Docker', link: '/guide/docker' }
          ]
        },
        {
          text: 'Using BrandKit',
          items: [
            { text: 'The generation workflow', link: '/guide/usage' },
            { text: 'Output formats', link: '/guide/formats' },
            { text: 'Image preprocessing', link: '/guide/preprocessing' },
            { text: 'Background removal', link: '/guide/background-removal' },
            { text: 'Keyboard shortcuts', link: '/guide/keyboard-shortcuts' }
          ]
        },
        {
          text: 'Operating it',
          items: [
            { text: 'Deployment', link: '/guide/deployment' },
            { text: 'Performance & caching', link: '/guide/performance' },
            { text: 'Troubleshooting', link: '/guide/troubleshooting' }
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'Configuration', link: '/reference/configuration' },
            { text: 'Environment variables', link: '/reference/environment' },
            { text: 'HTTP endpoints', link: '/reference/http-api' },
            { text: 'Format catalogue', link: '/reference/format-catalogue' },
            { text: 'Changelog', link: '/reference/changelog' }
          ]
        }
      ],
      '/': [
        {
          text: 'Project',
          items: [
            { text: 'Guide', link: '/guide/' },
            { text: 'Reference', link: '/reference/configuration' },
            { text: 'Security policy', link: '/security' },
            { text: 'Privacy', link: '/privacy' },
            { text: 'Contributing', link: '/contributing' },
            { text: 'Code of conduct', link: '/code-of-conduct' }
          ]
        }
      ]
    },

    socialLinks: [{ icon: 'github', link: REPO }],

    editLink: {
      pattern: REPO + '/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },

    lastUpdated: {
      text: 'Last updated',
      formatOptions: { dateStyle: 'medium' }
    },

    search: {
      provider: 'local',
      options: {
        detailedView: true
      }
    },

    outline: { level: [2, 3], label: 'On this page' },

    footer: {
      message:
        'Released under the <a href="' + REPO + '/blob/main/LICENSE">MIT License</a> · ' +
        '<a href="/brandkit/privacy">Privacy</a> · ' +
        '<a href="/brandkit/security">Security</a> · ' +
        '<a href="/brandkit/.well-known/security.txt">security.txt</a> · ' +
        '<a href="/brandkit/llms.txt">llms.txt</a>',
      copyright: 'Copyright © 2025–present Fabrizio Salmi'
    },

    docFooter: { prev: 'Previous', next: 'Next' }
  }
})
