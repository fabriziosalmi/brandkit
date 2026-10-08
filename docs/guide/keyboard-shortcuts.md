---
title: Keyboard shortcuts
description: Complete keyboard shortcut reference for the BrandKit interface.
---

# Keyboard shortcuts

Press <kbd>Shift</kbd>+<kbd>?</kbd> or <kbd>⌘</kbd>+<kbd>K</kbd> anywhere in the application to display the shortcuts dialog.

| Shortcut | Context | Action |
| --- | --- | --- |
| <kbd>⌘</kbd>+<kbd>V</kbd> / <kbd>Ctrl</kbd>+<kbd>V</kbd> | Global | Ingest master image from system clipboard |
| <kbd>Space</kbd> | Drop zone focused | Open native file selector |
| <kbd>⌘</kbd>+<kbd>Enter</kbd> / <kbd>Ctrl</kbd>+<kbd>Enter</kbd> | Global | Trigger generation pipeline |
| <kbd>Esc</kbd> | Global | Cancel processing, dismiss modal, or reset form |
| <kbd>⌘</kbd>+<kbd>K</kbd> / <kbd>Shift</kbd>+<kbd>?</kbd> | Global | Toggle shortcuts modal |

## Detailed behavior

### Clipboard ingestion (<kbd>⌘</kbd>+<kbd>V</kbd> / <kbd>Ctrl</kbd>+<kbd>V</kbd>)

Ingests PNG or JPEG image data directly from the OS clipboard into the master staging area, triggering metadata analysis and live telemetry extraction immediately.

### File selection (<kbd>Space</kbd>)

Opens the OS file picker dialog when the master upload area has keyboard focus. Navigate to the drop zone using <kbd>Tab</kbd>.

### Pipeline execution (<kbd>⌘</kbd>+<kbd>Enter</kbd> / <kbd>Ctrl</kbd>+<kbd>Enter</kbd>)

Initiates batch generation when the following preconditions are met:

1. Master image is loaded in staging
2. At least one canvas format is selected
3. At least one output encoding is checked
4. An active generation cycle is not already running

### Escape handling (<kbd>Esc</kbd>)

Evaluates application state contextually in priority order:

1. Close shortcuts dialog if open
2. Clear format filter query if search input is populated
3. Cancel running batch generation request
4. Reset upload state and return to staging view

## Accessibility standards

The interface is engineered for non-mouse operation:

- Every interactive control is sequenced in logical <kbd>Tab</kbd> order.
- Focused states render high-contrast hairline focus rings.
- Form inputs and status indicators provide semantic ARIA labels.
- Synchronous inline scripts eliminate theme and layout shifts before Alpine.js hydration.

## Browser compatibility

Tested across Chromium, Firefox, and Safari on macOS and Linux. If a shortcut conflicts with browser or system-level intercepts (e.g. extension shortcuts), clicking the corresponding interface control remains functional.
