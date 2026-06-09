---
layout: post
title: "I Built MCP Servers for 9 SaaS APIs — Here's What I Learned About the Pattern"
date: 2026-06-08
banner:
  image: /assets/images/covers/marvin-meyer-SYTO3xs06fU-unsplash.jpg
author: zane.deng
categories: [AI Coding]
tags: [MCP, AI Agent, API Integration, TypeScript, Tool Design]
---

Over the past few weeks, I built MCP servers for 9 APIs: CoinGecko, Stripe, Jira, PostHog, Plausible, Etherscan, DeFiLlama, Jobber, and Resend. 9 servers, 68 tools, all published to npm and indexed on Glama.

In doing so, I noticed the same architecture working again and again. If you're building MCP servers for your own API — or considering hiring someone to — here's what I learned.

## The Three-Layer Architecture

Every MCP server I built contains three layers:

### 1. Tool Definitions (Contract Layer)

Each API endpoint maps to an MCP tool with a typed input schema. I use Zod for validation — it catches bad inputs before they reach your API.

```typescript
{
  name: "send_email",
  description: "Send a single email via Resend",
  inputSchema: {
    from: z.string().email(),
    to: z.union([z.string().email(), z.array(z.string().email())]),
    subject: z.string().min(1),
    html: z.string().optional(),
    text: z.string().optional(),
  },
}
```

**The importance of description goes beyond what you'd expect**. LLMs use these descriptions to decide which tool to call. Vague descriptions like "send email" waste tokens. Specific ones like "Send a single transactional email via Resend API. Supports HTML and plain text. Returns message ID and delivery status." ensure the tool gets used correctly.

### 2. API Client (Plumbing Layer)

This layer handles authentication, rate limiting, and error translation. Key insight: **Don't leak HTTP errors to the LLM**. Convert them into structured, actionable error messages.

```typescript
// Bad: "Error: 429"
// Good: "Rate limited by Resend API. Retry after 30 seconds. You've sent 100 emails in the last hour."
```

### 3. Output Formatter (Presentation Layer)

Raw JSON dumps are terrible for LLMs. Format responses as Markdown tables, bullet points, or structured text. LLMs decide their next steps by reading output — make it scan-friendly.

```
## Email Sent Successfully
- **Message ID:** abc123
- **From:** alerts@yourcompany.com
- **To:** user@example.com
- **Subject:** Your weekly report
- **Status:** Queued for delivery
```

## Patterns That Worked Repeatedly

### Mock Mode

Every server includes a mock mode that returns realistic fake data. This lets developers test without real API credentials. It's also how I tested during development — no API keys needed.

### Progressive Disclosure

If the LLM only needs 3 tools, don't expose all 18 at once. Group tools by use case. The Resend server has tools for emails, contacts, domains, and API keys — developers sending emails don't need to see domain management tools.

### Error Recovery

APIs fail, networks timeout, rate limits trigger. Servers should handle retries internally and tell the LLM how long to wait in error messages.

## Best Practices for Tool Design

1. **Be specific with descriptions**: Explain input format, constraints, and what comes back
2. **Use Zod for input validation**: Catch errors before they reach the API
3. **Unify error formats**: Let the LLM know how to handle failures
4. **Return readable output**: Markdown tables beat raw JSON
5. **Include mock mode**: Makes testing and development easier

## Published MCP Servers

| Server | Tools | Platform |
|--------|-------|----------|
| @friendlygeorge/mcp-resend | Email, contacts, domains, API keys | Resend |
| @friendlygeorge/mcp-stripe | Payments, subscriptions, customers | Stripe |
| @friendlygeorge/mcp-jira | Issues, projects, workflows | Jira |
| @friendlygeorge/mcp-coingecko | Crypto prices, market data | CoinGecko |
| @friendlygeorge/mcp-etherscan | Blockchain queries, contracts | Etherscan |
| @friendlygeorge/mcp-plausible | Analytics, visitors | Plausible |
| @friendlygeorge/mcp-posthog | Events, users, cohorts | PostHog |
| @friendlygeorge/mcp-defillama | DeFi protocols, TVL | DeFiLlama |
| @friendlygeorge/mcp-jobber | Jobs, clients, quotes | Jobber |

All servers are published to npm and indexed on Glama for developers to find and reference.


*Source: https://dev.to/friendlygeorge/i-built-mcp-servers-for-9-saas-apis-heres-what-i-learned-about-the-pattern-2mf7*