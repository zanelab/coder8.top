---
layout: post
title: "I Built MCP Servers for 9 SaaS APIs — Here's What I Learned About the Pattern"
date: 2026-06-08
banner:
  image: /assets/images/covers/freestocks-I_pOqP6kCOI-unsplash.jpg
author: zane.deng
categories: [AI Coding]
tags: [MCP, AI Coding, TypeScript, Zod, API]
---


Over the past few weeks, I built MCP servers for 9 APIs: CoinGecko, Stripe, Jira, PostHog, Plausible, Etherscan, DeFiLlama, Jobber, and Resend. Nine servers, 68 tools, all published to npm and indexed on Glama.

Through this process, I noticed the same architecture patterns working repeatedly. If you're building MCP servers for your own APIs—or thinking about hiring someone to do it—here's what I learned.

## The Three-Layer Architecture

Every MCP server I built follows the same three-layer separation:

### Layer 1: Tool Definition (Contract Layer)

Each API endpoint maps to one MCP tool with a typed input schema. I use **Zod** for runtime validation—it catches bad input before it reaches your API, which is more suitable for LLM calling patterns than TypeScript's compile-time checks.

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

> 💡 **Descriptions matter more than you'd think.** LLMs use these descriptions to decide which tool to call. Vague descriptions like `send email` waste tokens. Specific ones like `"Send a single transactional email via Resend API. Supports HTML and plain text. Returns message ID and delivery status."` get the right tool selected.

### Layer 2: API Client (Plumbing Layer)

This layer handles authentication, rate limiting, and error transformation. **Key insight: Don't leak HTTP errors to the LLM.** Convert them into structured, actionable error messages:

```typescript
// ❌ Bad: "Error: 429"
// ✅ Good: "Rate limited by Resend API. Retry after 30 seconds. You've sent 100 emails in the last hour."
```

### Layer 3: Output Formatter (Presentation Layer)

Raw JSON dumps are terrible for LLMs. Format responses as Markdown tables, bullet points, or structured text. The LLM decides its next step by reading the output—make it scannable:

```
## Email Sent Successfully
- **Message ID:** abc123
- **From:** alerts@yourcompany.com
- **To:** user@example.com
- **Subject:** Your weekly report
- **Status:** Queued for delivery
```

## Three Patterns That Repeatedly Work

### 1. Mock Mode

Every server includes a mock mode that returns realistic fake data. This lets developers test without real API credentials. It's also how I tested during development—no API key needed.

### 2. Progressive Disclosure

If the LLM only needs 3 tools, don't expose all 18 at once. **Group tools by use case.** Developers sending emails don't need to see domain management tools:

| Server | Tool Groups |
|--------|-------------|
| Resend | Email, Contacts, Domains, API Keys |
| Stripe | Payments, Subscriptions, Customers |
| Jira | Issues, Projects, Workflows |

### 3. Error Recovery

APIs fail, networks timeout, rate limits trigger. The server should handle retries internally and tell the LLM how long to wait in the error message, rather than exposing raw error codes.

## 5 Best Practices for Tool Design

1. **Be specific in descriptions**: Explain input formats, constraints, and return values
2. **Use Zod for input validation**: Catch errors before data reaches the API
3. **Standardize error formats**: Let the LLM know how to handle failures
4. **Return readable output**: Markdown tables beat raw JSON
5. **Include mock mode**: Makes testing and development easier

## Published MCP Servers

| Server | Tools | Platform |
|--------|-------|----------|
| @friendlygeorge/mcp-resend | Email, Contacts, Domains, API Keys | Resend |
| @friendlygeorge/mcp-stripe | Payments, Subscriptions, Customers | Stripe |
| @friendlygeorge/mcp-jira | Issues, Projects, Workflows | Jira |
| @friendlygeorge/mcp-coingecko | Crypto prices, Market data | CoinGecko |
| @friendlygeorge/mcp-etherscan | Blockchain queries, Contracts | Etherscan |

All servers are published to npm and indexed on Glama for developers to find and reference.

---

*Source: https://dev.to/friendlygeorge/i-built-mcp-servers-for-9-saas-apis-heres-what-i-learned-about-the-pattern-2mf7*
