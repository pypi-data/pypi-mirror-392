# docpull

**Pull documentation from ANY website and convert to clean, AI-ready markdown.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/docpull.svg)](https://badge.fury.io/py/docpull)
[![License: MIT](https://img.shields.io/github/license/raintree-technology/docpull)](https://github.com/raintree-technology/docpull/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

## Why docpull?

Unlike wget or httrack that dump messy HTML, **docpull extracts clean markdown** perfect for:
- Training AI models / RAG systems
- Building knowledge bases
- Creating searchable documentation archives
- Offline documentation reading

**Production-ready**: Full type safety (mypy), security scanning (Bandit), zero linting issues (Ruff), comprehensive test coverage, and no known vulnerabilities.

## Features

- **Universal**: Scrape ANY documentation site - not limited to predefined sources
- **Smart extraction**: Auto-detects main content, removes navigation/ads
- **Blazing fast**: Async/parallel fetching (10x faster than sync)
- **JavaScript support**: Handles JS-heavy sites with Playwright
- **Progress bars**: Beautiful real-time progress with Rich
- **Sitemap support**: Auto-discovers pages via sitemap.xml
- **Link crawling**: Optionally follows links to discover all pages
- **Secure**: Rate limiting, content validation, timeout controls
- **Clean output**: Markdown with YAML frontmatter
- **Configurable**: Control depth, page limits, concurrency
- **Resumable**: Skip already-fetched files

## Quick Start

```bash
# Install
pip install docpull

# Scrape ANY documentation site
docpull https://aptos.dev
docpull https://docs.anthropic.com
docpull https://go.dev/doc

# Use optimized profiles for popular sites
docpull stripe
docpull nextjs react

# Control scraping behavior
docpull https://newsite.com/docs --max-pages 100 --max-concurrent 20
```

## Installation

```bash
# Basic installation
pip install docpull

# With YAML config support
pip install docpull[yaml]

# With JavaScript rendering (for JS-heavy sites)
pip install docpull[js]
python -m playwright install chromium

# Everything
pip install docpull[all]
python -m playwright install chromium
```

## Usage

### Scrape Any URL

The primary way to use docpull is by providing any documentation URL:

```bash
# Single site
docpull https://aptos.dev

# Multiple sites
docpull https://aptos.dev https://docs.soliditylang.org

# Control crawling
docpull https://docs.example.com \
  --max-pages 200 \
  --max-depth 4 \
  --rate-limit 1.0
```

### Use Optimized Profiles

For popular documentation sites, use shortcut names for optimized scraping:

```bash
# Single profile
docpull stripe

# Multiple profiles
docpull stripe plaid nextjs

# Mix profiles and URLs
docpull stripe https://newsite.com/docs
```

### JavaScript Rendering

For sites that require JavaScript to render content:

```bash
# Enable JS rendering with Playwright
docpull https://js-heavy-site.com --js

# Combine with other options
docpull https://site.com --js --max-pages 50 --max-concurrent 5
```

**Note:** JS rendering is slower but handles modern SPAs and dynamically-loaded content.

### Available Profiles

| Profile | Site | Optimizations |
|---------|------|---------------|
| `stripe` | docs.stripe.com | Filters changelog, focused on API docs |
| `nextjs` | nextjs.org | Excludes blog/showcase, docs only |
| `react` | react.dev | Learn & reference sections only |
| `plaid` | plaid.com | API + guides, excludes marketing |
| `tailwind` | tailwindcss.com | Documentation only |
| `bun` | bun.sh | Runtime documentation |
| `d3` | d3js.org | Data visualization docs |
| `turborepo` | turbo.build | Monorepo tooling docs |

### Python API

```python
from docpull import GenericAsyncFetcher

# Scrape any URL (async/parallel)
fetcher = GenericAsyncFetcher(
    url_or_profile="https://aptos.dev",
    output_dir="./docs",
    max_pages=100,
    max_concurrent=20,
    use_js=False,  # Set to True for JS rendering
)
fetcher.fetch()

# Or use a profile
fetcher = GenericAsyncFetcher(
    url_or_profile="stripe",
    output_dir="./docs",
)
fetcher.fetch()
```

### Advanced Options

```bash
# Limit pages and depth
docpull https://docs.example.com --max-pages 50 --max-depth 2

# Control concurrent requests (default: 10)
docpull https://site.com --max-concurrent 20

# Enable JavaScript rendering
docpull https://site.com --js

# Custom output directory
docpull stripe --output-dir ./my-docs

# Adjust rate limiting
docpull https://site.com --rate-limit 2.0

# Re-fetch existing files
docpull stripe --no-skip-existing

# Verbose logging
docpull https://site.com --verbose

# Disable progress bars
docpull https://site.com --no-progress

# Dry run (see what would be fetched)
docpull https://site.com --dry-run
```

## Performance

**Async/Parallel Fetching** makes docpull **10x faster** than traditional sync scrapers:

| Pages | Sync (old) | Async (new) | Speedup |
|-------|-----------|-------------|---------|
| 5 | ~5.0s | ~1.8s | 2.8x faster |
| 50 | ~50s | ~6s | 8.3x faster |
| 500 | ~500s | ~45s | 11x faster |

With `--max-concurrent 20`, even faster for large sites!

## Output Format

Each page is saved as markdown with YAML frontmatter:

```markdown
---
url: https://stripe.com/docs/payments
fetched: 2025-11-13
---

# Payment Intents

Your clean documentation content here...
```

Files are organized by URL structure:

```
docs/
├── stripe/
│   ├── api/
│   │   ├── charges.md
│   │   └── customers.md
│   └── payments/
│       └── payment-intents.md
└── aptos_dev/
    ├── guides/
    │   └── getting-started.md
    └── reference/
        └── api.md
```

## How It Works

1. **Discovery**: Tries sitemap.xml first, falls back to link crawling
2. **Filtering**: Applies URL patterns to focus on documentation
3. **Extraction**: Removes nav/footer/ads, extracts main content
4. **Conversion**: Converts HTML to clean markdown
5. **Organization**: Saves with structure that mirrors the site
6. **Async Magic**: Fetches multiple pages concurrently with rate limiting

## Configuration File

Create `config.yaml` for complex setups:

```yaml
output_dir: ./docs
rate_limit: 0.5
skip_existing: true
log_level: INFO

sources:
  - stripe
  - nextjs
  - react
```

Run with:
```bash
docpull --config config.yaml
```

## Creating Custom Profiles

You can create optimized profiles for your frequently-scraped sites:

```python
from docpull.profiles.base import SiteProfile

MY_PROFILE = SiteProfile(
    name="mysite",
    domains={"docs.mysite.com"},
    sitemap_url="https://docs.mysite.com/sitemap.xml",
    base_url="https://docs.mysite.com/",
    include_patterns=["/docs/", "/api/"],
    exclude_patterns=["/blog/"],
    output_subdir="mysite",
    rate_limit=0.5,
)
```

## Security

docpull is designed with security in mind:

- **HTTPS-only** by default
- **Private IP blocking** (no localhost, 192.168.x.x, etc.)
- **Content size limits** (50MB max per page)
- **Timeout controls** (30s per request)
- **Rate limiting** (async-safe, prevents DoS)
- **Concurrent connection limits** (prevents overwhelming servers)
- **Content-type validation** (only fetches HTML/XML)
- **Playwright sandboxing** (when using --js)

See [SECURITY.md](SECURITY.md) for detailed security information.

## Comparison with Alternatives

| Tool | Output | Works on any site? | Clean extraction? | Speed | JS Support |
|------|--------|-------------------|-------------------|-------|------------|
| **docpull** | Clean markdown | Yes | Yes | Fast (async) | Optional |
| wget | Raw HTML | Yes | No | Slow (sync) | No |
| httrack | Raw HTML | Yes | No | Slow (sync) | No |
| Site-specific | Varies | No | Varies | Varies | No |

## Troubleshooting

### Site requires JavaScript

```bash
# Install Playwright support
pip install docpull[js]
python -m playwright install chromium

# Use --js flag
docpull https://site.com --js
```

### Too slow / rate limited

```bash
# Reduce concurrent requests
docpull https://site.com --max-concurrent 5 --rate-limit 2.0
```

### Memory issues on large sites

```bash
# Limit pages fetched
docpull https://site.com --max-pages 1000
```

## Contributing

Contributions welcome! To add:
- **New site profiles**: Create a profile in `docpull/profiles/`
- **Better extraction**: Improve content detection in `fetchers/base.py`
- **Performance improvements**: Optimize async fetching
- **Bug reports**: Use the [issue tracker](https://github.com/raintree-technology/docpull/issues)

### Development Setup

```bash
# Clone and install
git clone https://github.com/raintree-technology/docpull
cd docpull
pip install -e ".[dev]"

# Run all quality checks (as per CI)
black --check .           # Code formatting
ruff check .              # Linting
mypy docpull              # Type checking
bandit -r docpull         # Security scanning
pip-audit                 # Dependency vulnerabilities
pytest --cov=docpull -v   # Tests with coverage
```

All PRs must pass these checks before merging.

## Documentation

- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Links

- [PyPI](https://pypi.org/project/docpull/)
- [GitHub](https://github.com/raintree-technology/docpull)
- [Issues](https://github.com/raintree-technology/docpull/issues)
