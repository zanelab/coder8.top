---
layout: post
title: "Ask HN: Current best open-source or commercial automated LLM coding agent?"
subtitle: ""
banner:
  image: /assets/images/posts/20260604080141-6a22b8e0.jpg
  opacity: 0.7
author: zane.deng
categories: [AI Coding]
tags:
- AI Coding
- Translation
- hackernews
---

# The Human in the Loop: LLM Coding Agents, Compiler Feedback, and the State of Automated Code Generation

## Introduction

A Hacker News thread asked a deceptively simple question: which open-source or commercial automated LLM coding agent is best for day-to-day work in 2026? The original post accumulated a modest score and only a handful of comments, but the substance cuts to a deeper problem — the gap between code *generation* and code *verification*. This rewrite unpacks what the thread said, what it omitted, and what the answers reveal about the AI-assisted programming ecosystem.

## The Original Post: A Working Developer's Frustration

The poster, "eigenvalue," opens by surveying the editor market — VS Code with GitHub Copilot or SuperMaven, Cursor, the open-source Void, Pear — and immediately rejects the premise that an AI-native IDE is necessary. They prefer ChatGPT and Claude in the browser alongside vanilla VS Code. This is itself a data point: the integrated AI IDE had not yet won the workflow argument for at least one experienced practitioner.

The core complaint is operational, not philosophical. The poster describes an exhausting micro-loop:

1. Ask the LLM to generate a code block or whole file.
2. Paste it into the editor.
3. Read the linter output (Ruff for Python, ESLint for TypeScript).
4. Copy the error messages back into the LLM as a follow-up.
5. Repeat, occasionally substituting `bun run build` or `cargo build` output for editor diagnostics.

The poster explicitly identifies themselves as "the one closing the loop between the LLM and the compiler/interpreter." Flagship commercial models, they note, are already strong on standard-library code in Python and TypeScript, and the typical failures are TypeScript type errors and incorrect npm/pip library APIs. They concede that lint-clean compilation is not the same as correctness — "you need to really run things end-to-end with real data" — but argue that catching the mechanical failures automatically would eliminate huge churn.

The post closes by invoking Devin AI, the autonomous software-engineering agent whose demo video had circulated earlier in 2024, as the conceptual ideal: an agent that closes the generation-and-verification loop and iteratively refines code until the linter, the compiler, and the tests all pass.

## The Comment Thread: A Sparse but Revealing Signal

Only three comments landed. One was later deleted. Of the other two, `sargstuff` recommends **Zed** (zed.dev), the Rust-based editor with built-in AI integration, and then posts a sprawling link dump: tree-sitter code views, VS Code problem-matchers, a Python venv tutorial, Dockside, an Ansible-versus-Jenkins comparison, Nitric, two pieces on Emacs TypeScript tooling, and a Neovim news roundup. The comment reads less as a recommendation than as a "tools I think about" scratchpad. The implicit thesis is that no single agent solves the loop problem; the solution is a constellation of editors, language servers, and build pipelines that the developer orchestrates manually.

`syndicatedjelly` offers the most candid assessment: **Codeium** has "stuck the longest" for them, despite being "rough around the edges." The commenter attributes this either to underfunding or to a team that prioritizes the core engine over polish. It is a sophisticated read — the moat in AI coding tools is not the chat surface but model quality on the long tail of real code, and a scrappy competitor can out-iterate a well-funded incumbent if it stays focused on inference.

## What the Thread Is Really About

Read as a whole, the thread is not a buyer's guide. It is an artifact of a transitional moment. The poster correctly diagnoses the central problem of agentic coding — the verification loop — and correctly identifies Devin as the leading exemplar of a class of systems trying to close that loop. But the comments do not endorse Devin. They endorse Zed (an editor) and Codeium (a completion engine), both of which *assist* the developer rather than *replace* the developer's role as verifier. The thread captures the moment the community is still waiting for the autonomous agent to mature, and is settling for tool-augmented human verification in the meantime.

## The 2026 Landscape: What Changed and What Did Not

Two years on, the taxonomy has solidified into four tiers:

- **Inline completion engines** — Copilot, Codeium, Tabnine, and the open-source Continue. The highest-ROI tools for most developers, integrated into the editor with a low cognitive cost per suggestion.
- **IDE-integrated chat and edit agents** — Cursor, Windsurf, Zed's assistant panel, VS Code's Copilot Chat. A conversational surface and, in the more capable variants, a multi-file agent mode.
- **Repository-level autonomous agents** — Devin, SWE-Agent, OpenHands, Aider, Claude Code. These accept a high-level task, plan, edit, run tests, observe failures, and iterate. They are the direct descendants of the capability the original poster was asking about.
- **Pre-commit and policy enforcers** — tools like Agentic Gatekeeper that do not generate code but instead audit staged changes against a written rule set and auto-patch violations. They occupy the QA niche, not the generation niche.

The original poster's specific pain — copying compiler errors back into a chat — is now largely addressed by editor-integrated agents that read the Problems panel and the terminal output themselves. The deeper problem the poster acknowledged — end-to-end testing with real data — remains the hard frontier, and is the active research direction in SWE-Bench-style evaluation and reinforcement learning from execution feedback.

`sargstuff`'s link dump now reads as a period piece: much of the bespoke editor-and-build orchestration has been absorbed into agents that do it for you. `syndicatedjelly`'s observation about Codeium, however, has aged into a general truth: model quality on real repositories is the moat, and companies that treat it as the moat (Anthropic, the Cursor team, Cognition) have outlasted those that treated UX polish as the moat.

## Conclusion

The thread is small — one point, two visible comments, one deleted — but unusually precise in framing the problem of automated code generation. The poster correctly identifies the verification loop, correctly identifies Devin as the leading attempt to close it, and correctly observes that flagship LLMs are already strong enough that the bottleneck is feedback rather than generation. The community responses, recommending Zed and Codeium, reflect the practical reality of mid-decade tooling: the autonomous agent has not yet won the workflow, and most developers still want a fast completion engine and a competent chat surface inside an editor they already know. In 2026, the gap has narrowed but not closed. Repository-level agents can iterate against a real test suite, but they still hallucinate APIs, still over-edit, and still require a human reviewer who can read a diff. The most interesting new category — pre-commit policy enforcers — exists precisely because someone still has to be the gatekeeper at the end of the loop, even when the agent in the middle has done good work. The original poster's instinct, that lint-and-compile is not enough, has been vindicated; the system that finally closes the loop end-to-end is still being built.
