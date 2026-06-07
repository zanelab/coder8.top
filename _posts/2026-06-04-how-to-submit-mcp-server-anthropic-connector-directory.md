---
layout: post
title: "How to Submit Your MCP Server to Anthropic's Connector Directory"
date: 2026-06-04
banner:
  image: /assets/images/covers/luca-bravo-XJXWbfSo2f0-unsplash.jpg
author: zane.deng
categories: [AI Coding]
tags: [MCP, Claude, Anthropic, Developer Tools]
---

> A practitioner's guide based on real submission experience — form details, review pitfalls, and the3 big mistakes I made so you don't have to.

---

## Why Bother with the Connector Directory?

When your MCP server isn't in the directory, users need to:

1. Go to Claude Settings → Connectors
2. Click "Add Custom Connector"
3. Manually paste the server URL
4. Authenticate

That's four friction-filled steps. Most non-developer users won't bother.

Once your server is listed, users find you in the list, click **Connect**, and authorize — same OAuth flow, zero tedious steps.

The directory is also how Anthropic surfaces integrations to **Claude Pro and Team users** who never look at developer docs. For a SaaS product, that's a meaningful passive distribution channel.

---

## Three Types You Can Submit

| Type | Description | Form Difference |
|------|-------------|----------------|
| **Remote MCP Server** | Internet-hosted server with tools, resources, prompts | Standard form |
| **Desktop Extension** | Local MCP server packaged as `.bundle` for Claude Desktop | Extra bundling required |
| **MCP App** | MCP server rendering interactive UI inside chat | 3-5 screenshots required (min 1000px wide) |

This guide covers the **Remote MCP Server** path.

---

## The Submission Form: What It Actually Asks

### Section 1: Basic Server Info

| Field | Requirement | Common Mistake |
|-------|-----------|----------------|
| Server Name | ≤ 64 characters, English | Name too long or has special chars |
| Tagline | 1-2 sentence description | Vague marketing copy |
| Server URL | Must support **streaming HTTP** (SSE no longer accepted) | Using SSE endpoint |
| Connector Type | remote / desktop / MCP app | Wrong type selected |
| Primary Use Cases | 2-3 sentences in English | Chinese description / essay-length list |

### Section 2: Connection Details

```
Transport: Streaming HTTP required (SSE deprecated)
Auth Type: OAuth 2.0 (recommended) / API Key / None
Read/Write: read tools and write tools must be listed separately
Callback URL: OAuth callback URL must be registered
```

**Critical issue:** SSE (Server-Sent Events) is officially deprecated. Anthropic now requires streaming HTTP. If your server uses SSE, migrate to [MCP streaming HTTP](https://modelcontextprotocol.io/docs/http).

### Section 3: Tools and Resources

Every tool needs:
- Human-readable title
- **Annotation** (metadata describing what the tool does)
- Tool name ≤ 64 characters
- **read and write tools must be separate**

```python
# WRONG: read/write mixed
"tools": [
    {"name": "qr_create", "annotations": {"read": True, "write": True}}
]

# CORRECT: separate declarations
"tools": [
    {"name": "qr_create", "annotations": {"read": True, "write": False}},
    {"name": "qr_delete", "annotations": {"read": False, "write": True}}
]
```

### Section 4: Documentation

- Public docs URL (a single help page or blog post is fine)
- **At least 3 example prompts** exercising different tools
- Setup and auth steps
- You can share a private staging link during review if docs aren't public yet

### Section 5: Privacy & Compliance

| Field | Requirement |
|-------|------------|
| Privacy Policy URL | Must be publicly accessible |
| Data Handling | What you collect, how long you keep it, who you share it with |
| Security | HTTPS verification + Origin header validation |

### Section 6: Test Account & Branding

- **Test account**: Login credentials with realistic sample data
- **Logo**: Server logo (URL or SVG)
- **Favicon**: Site favicon
- MCP App only: 3-5 PNG screenshots (min 1000px wide)

---

## Three Real Mistakes I Made

### Mistake 1: SSE Instead of Streaming HTTP

**Symptom:** Review email saying transport protocol unsupported.

**Root cause:** Many older MCP servers use SSE. Anthropic deprecated SSE in early 2026 in favor of streaming HTTP.

**Fix:** Upgrade your server to MCP streaming HTTP:

```python
# MCP streaming HTTP example (Python)
from mcp.server import MCPServer

server = MCPServer(
    name="my-mcp-server",
    tools=[qr_create_tool, qr_list_tool],
)
server.run(transport="streaming-http", port=3000)
```

### Mistake 2: Tool Name Over 64 Characters

**Symptom:** Review feedback: "tool name exceeds 64 characters".

**Fix:** Shorten tool names:

| Original | Revised | Characters |
|----------|---------|------------|
| `qr_code_generator_create_with_logo` | `qr_create` | 9 |
| `dynamic_qr_code_batch_delete` | `qr_batch_delete` | 15 |
| `qr_code_statistics_get_click_data` | `qr_stats` | 8 |

### Mistake 3: OAuth Callback URL Not Registered

**Symptom:** Users click Connect but OAuth authorization fails.

**Correct format:** `https://your-server.com/oauth/callback/anthropic`

Register this exact URL in your Anthropic Developer Console application settings before submitting.

---

## Post-Submission: Review Timeline

```
Day 1-2:   Automated format check (fail → immediate email)
Day 3-7:   Human technical review
Day 8-14:  Final approval + directory listing
```

---

## Pre-Submission Checklist

- [ ] Server URL uses streaming HTTP (not SSE)
- [ ] OAuth callback URL registered
- [ ] All tool names ≤ 64 characters
- [ ] read/write tools listed separately
- [ ] Each tool has annotation descriptions
- [ ] Public docs URL accessible
- [ ] ≥ 3 example prompts provided
- [ ] Privacy policy URL accessible
- [ ] Test account valid with sample data
- [ ] Logo and favicon ready

---

## Related Resources

- [Anthropic Connector Directory Submit Portal](https://connect.anthropic.com)
- [MCP Official Protocol Docs](https://modelcontextprotocol.io/docs/http)
- [QRflows MCP Server (real case study)](https://qrflows.com)

---

*This guide is based on QRflows team's real submission experience. The review is still in progress — updates will be added to the original article.*