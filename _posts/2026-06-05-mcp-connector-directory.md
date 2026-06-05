---
layout: post
title: "How to Submit Your MCP Server to Anthropic's Connector Directory"
date: 2026-06-05
categories:
  - AI Coding
tags:
  - article
  - ai-coding
  - MCP
  - Claude
  - Anthropic
description: "A practical guide based on real submission experience — form details, review criteria, and pitfalls from my first attempt."
---

> A practical guide based on real submission experience — form details, review criteria, and pitfalls from my first attempt.

## Introduction

I built an MCP server for QRflows — a dynamic QR code platform. After the server was live and working, I submitted it to Anthropic's official Connector Directory.

The review is ongoing, but the process taught me things I couldn't find documented anywhere in one place.

This post covers the full submission process as it stands in mid-2026: what the form actually asks, the technical requirements that can silently kill your review, and how to prepare so you don't spend a week backtracking.

---

## Why Submit to the Connector Directory?

When your MCP server is not in the directory, users need to:

1. Open Claude Settings → Connectors
2. Click "Add Custom Connector"
3. Manually paste the server URL
4. Complete authentication

That's **four steps of copy-pasting**. Most non-developer users won't bother.

Once your server is in the directory, users simply find you in the list → click Connect → authorize. Same OAuth flow — but the tedious steps disappear.

The directory is also how Anthropic surfaces integrations to Claude Pro and Team users who never look at developer docs. For a SaaS product, that's a **significant distribution channel**.

---

## What Can Be Submitted?

The directory accepts three types:

| Type | Description |
|------|-------------|
| **Remote MCP Server** | An internet-hosted server with tools, resources, prompts |
| **Desktop Extension** | Local MCP server packaged as a `.bundle` for Claude Desktop |
| **MCP App** | An MCP server that renders interactive UI inside the chat (requires additional screenshots) |

> 💡 QRflows is a remote MCP server. The form and required assets differ by type — confirm which one you're submitting before you start.

---

## Submission Process

### Step 1: Pre-work — Gather These Before Opening the Form

Don't rush to open the form. First prepare:

**1. Server Basic Info**
- Server name and tagline
- Server URL
- Connector type (remote / desktop / MCP app)
- 2-3 sentence description of primary use cases

**2. Connection Details**
- Transport protocol (must be **Streaming HTTP**, SSE is no longer accepted)
- Authentication type
- Read/write capabilities
- Whether your OAuth callback URL is registered

**3. Tools and Resources**
- List every tool with a human-readable title
- Confirm annotations are in place
- Confirm read and write tools are separated
- Confirm tool names are ≤ 64 characters

**4. Documentation**
- At least one public documentation page (README or standalone page)

**5. Brand Assets**
- Logo (PNG/JPEG, clearly visible)
- At least one screenshot or demo image

> ⚠️ **Pitfall**: On my first submission, a tool name exceeded 64 characters and my review was rejected immediately. Always verify all tool name lengths before submitting.

---

### Step 2: Find the Correct Submission Form

The submission form is available through the Anthropic developer documentation under the Connector Directory section: **`https://docs.anthropic.com/en/latest/mcp/connector-directory`**

---

### Step 3: Wait for Review

- After submission, your server enters the **review queue**
- The Anthropic team reviews every field of your form and verifies your server actually conforms to MCP specifications
- If issues are found, they contact you via email (so double-check your email address)

---

## Key Checklist

| Item | Requirement |
|------|-------------|
| **Transport Protocol** | Streaming HTTP only — SSE is deprecated |
| **Tool Names** | Must be ≤ 64 characters |
| **Read/Write Separation** | Read tools and write tools must be defined separately |
| **OAuth** | Ensure callback URL is properly registered |
| **Documentation** | Must have a public documentation page |
| **Assets** | Prepare logo in PNG/JPEG and screenshots |

---

## Further Reading

- [Anthropic MCP Official Docs](https://docs.anthropic.com/en/latest/mcp)
- [MCP Connector Directory Submission](https://docs.anthropic.com/en/latest/mcp/connector-directory)
- [QRflows Dynamic QR Code Platform](https://qrflows.com)

---

*This article is based on real submission experience as of June 2026. Check official documentation for the most up-to-date information.*