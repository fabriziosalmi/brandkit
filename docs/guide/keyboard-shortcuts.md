---
title: Keyboard shortcuts
description: Every keyboard shortcut in the BrandKit interface.
---

# Keyboard shortcuts

Press <kbd>Shift</kbd>+<kbd>?</kbd> anywhere in the app to bring up this list in a dialog.

| Shortcut | Action |
| --- | --- |
| <kbd>Space</kbd> | Open the file selector, when the upload area has focus |
| <kbd>Ctrl</kbd>+<kbd>Enter</kbd> / <kbd>⌘</kbd>+<kbd>Enter</kbd> | Generate the brand kit |
| <kbd>Esc</kbd> | Reset the form, cancel processing, or close a dialog |
| <kbd>Shift</kbd>+<kbd>?</kbd> | Toggle the shortcuts dialog |

## Details

### <kbd>Space</kbd> — file selector

Opens the native file picker when the drop zone has keyboard focus. Reach it with <kbd>Tab</kbd> from the top of the page.

### <kbd>Ctrl</kbd>/<kbd>⌘</kbd>+<kbd>Enter</kbd> — generate

Submits the form. It only fires when all of these are true:

- a file has been uploaded
- at least one format is selected
- at least one output type is selected
- a generation is not already running

If nothing happens, one of those four is not satisfied.

### <kbd>Esc</kbd> — the universal back-out

Context-sensitive, in this priority order:

1. Shortcuts dialog open → close it
2. Format search active → clear the query
3. Processing in progress → cancel it
4. Results shown → reset the form and start over

### <kbd>Shift</kbd>+<kbd>?</kbd> — help

Toggles the shortcuts dialog. <kbd>Esc</kbd> also closes it.

## Accessibility

The interface is built for keyboard-only operation:

- every interactive element is reachable with <kbd>Tab</kbd>
- focus is visible — a 2 px blue outline with 2 px of offset on links, buttons and inputs
- controls carry ARIA labels for screen readers
- `[x-cloak]` prevents un-initialised Alpine markup from flashing before hydration

## Browser support

Chrome/Chromium, Firefox, Safari and Edge, current versions. If a shortcut does not fire, check whether an extension or the browser itself has claimed the combination — <kbd>Ctrl</kbd>+<kbd>Enter</kbd> in particular is contested by some password managers.
