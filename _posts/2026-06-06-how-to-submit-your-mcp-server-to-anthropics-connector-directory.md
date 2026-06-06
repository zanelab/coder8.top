---
layout: post
title: "How to Submit Your MCP Server to Anthropic's Connector Directory"
subtitle: ""
banner:
  image: /assets/images/posts/20260606000305-7b1f7aff.jpg
  opacity: 0.7
author: zane.deng
categories: [AI Coding]
tags:
- AI Coding
- Translation
- MCP
- Claude
---

title: "How to Submit Your MCP Server to Anthropic's Connector Directory"
source: "https://dev.to/qrflows/how-to-submit-your-mcp-server-to-anthropics-connector-directory-from-someone-who-did-it-143m"
date: 2026-06-04
tags:
  - article
  - ai-coding
  - mcp
  - claude
---

# How to Submit Your MCP Server to Anthropic's Connector Directory

## Background

I built an MCP server for [QRflows](https://qrflows.app) — a dynamic QR code platform. After the server was live and working, I submitted it to Anthropic's official Connector Directory. The review is ongoing, but the process taught me things I couldn't find documented anywhere in one place.

This post covers the full submission process as it stands in mid-2026: what the form actually asks, the technical requirements that can silently kill your review, and how to prepare so you don't spend a week backtracking.

---

## Why Submit to the Connector Directory?

When your MCP server isn't in the directory, users need to:
1. Go to Claude Settings → Connectors
2. Click "Add Custom Connector"
3. Manually paste the server URL
4. Complete authentication

That's four steps of copy-pasting. Most non-developer users won't bother.

Once your server is in the directory, users just find you in the list, click Connect, and authorize. Same OAuth flow — but the tedious steps disappear.

The directory is also how Anthropic surfaces integrations to Claude Pro and Team users who never look at developer docs. For SaaS products, that's a meaningful distribution channel.

---

## What You Can Submit

The directory accepts three types:

| Type | Description |
|------|-------------|
| Remote MCP Server | An internet-hosted server with tools, resources, prompts |
| Desktop Extension | Local MCP server packaged for Claude Desktop |
| MCP App | MCP server that renders interactive UI inside the chat (needs extra screenshots) |

QRflows is a remote MCP server. The form and required assets differ by type, so confirm which one you're submitting before you start.

---

## What the Submission Form Actually Asks

The form is at [Anthropic's official page](https://claude.ai/connector-directory). It's not short. Here's what each section covers so you can prepare everything before you open it:

### 1. Basic Server Information

- Name, tagline
- Server URL
- Connector type (remote / desktop / MCP app)
- Primary use cases in 2–3 sentences

### 2. Connection Details

- Transport protocol (**must be streamable HTTP — SSE is no longer accepted**)
- Authentication type
- Read/write capabilities
- Whether your OAuth callback URL is registered

### 3. Tools and Resources

- List every tool with a human-readable title
- Confirm annotations are in place
- Confirm read and write tools are separate
- Confirm tool names are ≤ 64 chars

### 4. Documentation

- Public docs URL (a single help page or blog post is enough)
- Minimum 3 example prompts that exercise different tools
- Setup and auth steps

### 5. Privacy & Compliance

- Privacy policy URL
- Data handling summary (what you collect, how long you keep it, who you share it with)
- Confirmation of HTTPS and Origin-header validation

### 6. Test Account & Branding

- Login credentials for a test account with realistic sample data
- Server logo (URL or SVG)
- Favicon

---

## Technical Requirements That Trip People Up

### 1. Tool Annotations — The #1 Reason for Rejection

Every tool needs two things: a short `description` annotation and the right `security` hint.

```
// Tools missing annotations reportedly cause around 30% of all directory rejections.
```

The other mistake: don't bundle read and write into one generic tool. A tool called `manage_qrcode` with a `parameters` accepting `type`, `data`, `metadata`, `options` will fail review. Split them.

### 2. OAuth Callback URL

For the browser-based Claude (claude.ai), register exactly this redirect URI:

```
https://claude.ai/api/mcp/auth_callback
```

Claude Code uses a loopback redirect to `http://127.0.0.1` with an ephemeral port. If you want to support Claude Code users, your auth server needs to accept loopback redirects with the port ignored.

**PKCE is required.** Your authorization server metadata should declare PKCE support. Plain OAuth 2.0 without PKCE won't pass.

### 3. Origin-header Validation

Your MCP server must validate the `Origin` header and reject requests not coming from Claude. This is a security requirement, not optional.

### 4. Protected Resource Metadata

Claude uses this to discover your authorization server. Host it at:

```
https://your-server.com/.well-known/mcp-protected-resource.json
```

If this endpoint is missing, Claude can't complete OAuth discovery and the connector won't authenticate.

---

## Documentation Requirements

Anthropic wants docs that let a reviewer test your connector in 10 minutes without prior knowledge of your product. The minimum:

- What the connector does (2–3 sentences)
- How to connect step by step
- At least 3 example prompts that exercise different tools
- What the expected output looks like
- Privacy policy link

For QRflows I created `qrflows.app/mcp` as the dedicated docs page. A single well-organized page is enough.

---

## The Test Account

Create a separate account — not your main production account. Load it with realistic sample data. Write down the credentials before you open the form.

For QRflows I created a test account with 6–7 QR codes of different types (URL, WiFi, vCard, Smart Rules) so reviewers could test `list_qrcodes`, `get_qrcode`, and `create_qrcode` with real data.

If your tools operate on empty state, reviewers can't tell if they work or are broken.

---

## Review Timeline

Anthropic is upfront: they can't promise to review or respond to every submission individually because of volume. The typical timeline they cite is ~2 weeks, but it can run longer.

My submission has been in review for about a month. No response yet — from what I can tell that's within the normal range given submission volume right now.

While you're waiting: your server is already usable as a custom connector. Share the URL, write about it, put it in your docs. The directory listing is a distribution multiplier, not a prerequisite.

---

## What I'd Do Differently

**Read the submission guide before building.** Once I had the full list of requirements, I realized I was missing the Protected Resource Metadata endpoint and had to add it after the fact. Twenty minutes of reading upfront would have saved two hours.

**Load the test account before submitting.** I initially created a test account with no data. Reviewers testing `create_qrcode` would have seen an empty array with no way to tell if the tool worked.

**Write docs first.** The form asks for a public docs URL. If you don't have it ready, you have to pause. Write the docs page before you open the form.

---

## Submission Checklist

- [ ] Confirmed connector type (remote / desktop / MCP app)
- [ ] Every tool has `description` and `security` annotations
- [ ] Read/write tools split (not bundled in one tool)
- [ ] OAuth callback URL registered as `https://claude.ai/api/mcp/auth_callback`
- [ ] PKCE supported
- [ ] MCP server validates `Origin` header
- [ ] Protected Resource Metadata endpoint hosted
- [ ] Public docs page ready (minimum 3 example prompts)
- [ ] Test account created and loaded with real data
- [ ] Logo and Favicon ready

---

## Related Links

- [QRflows MCP Server](https://qrflows.app)
- [QRflows MCP Docs](https://qrflows.app/mcp)
- [Anthropic Connector Directory Submission Guide](https://claude.ai/connector-directory/submit)
- [MCP Spec](https://modelcontextprotocol.io)

---

*This article is based on real submission experience. The review result will be updated upon completion.*