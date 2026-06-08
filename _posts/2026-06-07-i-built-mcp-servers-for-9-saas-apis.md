---
layout: post
title: "I Built MCP Servers for 9 SaaS APIs — Here's What I Learned About the Pattern"
date: 2026-06-07
banner:
    image: /assets/images/covers/dmitry-chernyshov-mP7aPSUm7aE-unsplash.jpg
author: zane.deng
categories: [AI Coding]
tags: [article, ai-coding, MCP, AI Coding]
---

title: "I Built MCP Servers for 9 SaaS APIs — Here's What I Learned About the Pattern"
date: 2026-06-07
tags:
  - article
  - ai-coding
  - MCP
  - AI Coding
---


Over the past few weeks, I've been building MCP (Model Context Protocol) servers for various APIs — CoinGecko, Stripe, Jira, PostHog, Plausible, Etherscan, DeFiLlama, Jobber, and Resend. 9 servers, 68 tools, all published to npm and indexed on Glama. Throughout the building process, I noticed the same architecture kept repeating itself. If you're building an MCP server for your own API — or considering hiring someone to do it — here's a pattern.

## The Three-Layer Architecture

Every MCP server I built has three layers:

### 1. Tool Definitions (Contract)

Every API endpoint becomes an MCP tool with a typed input schema. I use Zod for validation — it catches bad inputs before they reach your API.

```javascript
{
  name: "send_email",
  description: "Send a single email via Resend",
  inputSchema: {
    from: z.string().email(),
    to: z.union([z.string().email(), z.array(z.string().email())]),
    subject: z.string().min(1),
    html: z.string().optional(),
    text: z.string().optional()
  }
}
```

### 2. API Client (Pipeline Layer)

This layer handles authentication, rate limiting, and error translation. Key insight: don't leak HTTP errors to the LLM. Convert them into structured, actionable error messages.

```javascript
// Bad: "Error: 429"
// Good: "Rate limited by Resend API. Retry after 30 seconds. You've sent 100 emails in the last hour."
```

### 3. Output Formatter (Presentation Layer)

Raw JSON dumps are hard for LLMs to use. Format responses as markdown tables, bullet points, or structured text. LLMs read this output to decide what to do next — make it scannable.

```markdown
## Email Sent Successfully

- **Message ID:** abc123
- **From:** alerts@yourcompany.com
- **To:** user@example.com
- **Subject:** Your weekly report
- **Status:** Queued for delivery
```

## Recurring Patterns

### Mock Mode

Every server includes a mock mode that returns realistic fake data. This lets developers test without live API credentials. It's also how I test during development — no API keys needed.

### Progressive Disclosure

If an LLM only needs 3 tools, don't dump all 18 tools on it at once. Group tools by use case. The Resend server has tools for emails, contacts, domains, and API keys — a developer sending emails doesn't need to see domain management tools.

### Error Recovery

APIs fail. Networks timeout. Rate limits trigger. The server should handle retries internally and provide clear "retry" instructions to the LLM, not raw stack traces.

## What I Deliver

When someone commissions me to build an MCP server, they get:

- A TypeScript MCP server with complete tool definitions
- Input validation via Zod schemas
- Structured error messages
- Clean markdown output optimized for LLM consumption
- A mock mode for testing without credentials
- Published to npm under their own scope (e.g., `@yourcompany/mcp-server`)
- Discoverable in the Glama/directory listing
- A README with installation instructions and tool directory

Typical delivery cycle: 1-3 days for a standard REST API.

## Why This Matters

MCP is becoming the standard way AI assistants connect to external services. Claude Desktop, Cursor, Windsurf, and other clients all support it. But most SaaS APIs don't have MCP servers yet. This gap means:

- Developers waste time switching between AI assistants and API dashboards
- APIs lose a distribution channel — appearing in an MCP directory is like being in an app store
- First-mover advantage — once an MCP server exists for an API, there's little reason to build a second

## Get In Touch

If your API needs an MCP server, I can build it. My portfolio includes servers for crypto (CoinGecko, Etherscan, DeFiLlama), analytics (PostHog, Plausible), project management (Jira, Jobber), payments (Stripe), and email (Resend).

GitHub: github.com/friendlygeorge

Tell me which API you need to connect. I'll give you scope and timeline within 24 hours.
