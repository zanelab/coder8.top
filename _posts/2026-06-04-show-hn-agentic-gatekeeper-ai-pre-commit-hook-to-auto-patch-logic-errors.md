---
layout: post
title: "Show HN: Agentic Gatekeeper – AI pre-commit hook to auto-patch logic errors"
subtitle: ""
banner:
  image: /assets/images/posts/20260604080148-3dbbea63.jpg
  opacity: 0.7
author: zane.deng
categories: [AI Coding]
tags:
- AI Coding
- Translation
- hackernews
---

# Agentic Gatekeeper: A Rule-Based Pre-Commit Agent for Enforcing Markdown-Defined Engineering Standards

## Overview

Agentic Gatekeeper is a Visual Studio Code extension, also distributed through Open VSX, that positions itself as an "autonomous AI agent" which enforces user-authored Markdown rules on every commit. The tagline — "Write rules in plain English → Stage your code → The Gatekeeper auto-patches violations before you push" — captures the workflow in a single sentence. The system is not a code generator, a chatbot, or an autonomous software engineer. It is a *policy enforcer* that sits between the developer's working tree and `git commit`, reading natural-language rules and applying targeted patches to staged files. The license is a modified MIT with a dedicated attribution clause.

## The Problem the Project Targets

The README articulates a familiar organizational pain point. Teams invest substantial effort in documenting engineering standards — architecture decisions, security guardrails, coding conventions, naming rules — and store them in standard files: `CONTRIBUTING.md`, `ARCHITECTURE.md`, or the more recent `AGENTS.md`. Yet the documents are passive. "Nobody enforces them." Whether the author is a human engineer or an AI coding assistant, rules silently drift, technical debt compounds, and pull-request review becomes a repetitive exercise in re-stating the same feedback. Agentic Gatekeeper's pitch is to convert these documents from advisory into enforced policy, automatically, before the code leaves the developer's machine.

## How the System Works

The end-to-end loop is intentionally simple. The developer stages changes in the VS Code Source Control panel, clicks a Shield icon or runs `Agentic Gatekeeper: Validate Rules` from the Command Palette, and the extension returns patched, re-staged files within seconds. Under the hood, the system collects three inputs: the staged diff, the set of applicable Markdown rule files, and (optionally) a remote rule repository. It sends the relevant subset of the diff to a configured language model, asks for a patch that satisfies the rules, and applies the result to the workspace.

Rules are plain Markdown. The README's example is a TypeScript architecture rule — "Every function must have an explicit return type..." — wrapped in YAML frontmatter that constrains the rule's scope via a `globs` pattern. The system supports three scopes: global rules in `.gatekeeper/*.md`, `AGENTS.md`, `ARCHITECTURE.md`, or `CONTRIBUTING.md`; directory-scoped rules named `*-instructions.md` or `*-gatekeeper.md` anywhere in the tree; and remote rules synced from a central GitHub repository into `.gatekeeper/remote/`. The remote-rules feature is notable: an organization can publish a canonical rule set and have every developer validate against the same source, with rules cached by SHA and stored under `.gitignore`.

A second command, `Agentic Gatekeeper: Validate Rules`, performs a meta-audit on the rules themselves. The system sends each rule to the model and asks for a structured report: an enforceability rating (`YES`, `PARTIALLY`, or `NO`), the target file types and directories, and side-by-side examples of code that violates and code that satisfies the rule. The intent is to let rule authors iteratively tighten vague prose — "prefer immutability" — into something the model can actually check for, such as "no function may mutate its arguments when the argument is a `readonly` interface."

## Engineering Internals Worth Noting

Several design choices respond directly to the failure modes of LLM-driven refactoring:

- **Streaming execution.** Patches apply in real time as batches resolve, reducing wall-clock latency for large changesets.
- **Intelligent patch mode.** For files larger than 200 lines, the system switches from whole-file rewrites to fuzzy search-and-replace, reducing the risk of accidental truncation.
- **Diff-only context.** For files larger than 1,000 lines, only the diff is sent to the model — a token-budget decision that also narrows the surface area for hallucinations.
- **Content-and-rule-version cache.** Re-runs on unchanged code are effectively instant, and editing a rule invalidates the cache for affected files.
- **`.gatekeeperignore` and built-in exclusions.** Standard dependency and build directories (`node_modules`, `dist`, `build`, `vendor`, `.next`, `venv`) are skipped automatically.
- **Safety check on patch application.** If a model-produced rewrite suspiciously reduces the file's byte count — a strong signal of truncation — the patch is rejected and the original file is preserved. The user can always `git diff` to inspect what changed before committing.

## Model and Provider Layer

The default execution path uses the developer's native IDE model — GitHub Copilot or Gemini — so the extension ships with zero required API keys. For higher-stakes rule sets, the user can configure an external provider: Anthropic (`claude-4.5-sonnet` named as the recommended high-reasoning model), OpenAI (`gpt-5.2`), Google Gemini (`gemini-3-pro`), OpenRouter (a bridge to DeepSeek, Llama, Grok, and hundreds of others), or any OpenAI-compatible local server such as Ollama or LM Studio. Local execution keeps code fully on-device, which is the privacy posture many enterprise teams require. OpenRouter users can configure referer and title headers for usage attribution.

The provider abstraction is a small but important architectural choice. It decouples the policy engine from any single model vendor, allowing a team to swap in a more capable model as the underlying ecosystem improves without rewriting the rule set or the patch logic.

## Position in the Broader AI Coding-Agent Landscape

The 2026 ecosystem is now stratified into several categories, and Agentic Gatekeeper occupies a niche distinct from each. Inline completion engines — Copilot, Codeium, Tabnine, Continue — operate at the keystroke level. IDE-integrated chat and edit agents — Cursor, Windsurf, Zed, Claude Code — provide a conversational surface and, in the more capable variants, a multi-file agent mode. Repository-level autonomous agents — Devin, SWE-Agent, OpenHands, Aider — accept a high-level task, plan, edit, run tests, and iterate. Agentic Gatekeeper does none of these. It is not generating code, not chatting about code, and not pursuing a goal. It is auditing staged changes against a written policy and applying minimal patches to bring the diff into compliance.

This makes it complementary to, rather than competitive with, the generative agents. A reasonable workflow is to use Cursor or Claude Code to implement a feature, then invoke Agentic Gatekeeper as the last step before commit, in the same way a team might run a linter, a formatter, and a security scanner. The Shield icon in the Source Control panel reinforces this parallel. It is pre-commit infrastructure, not generation infrastructure.

The deeper insight the project embodies is that natural-language rules are now expressive enough to be enforced. A rule like "every public API function must have a docstring that includes a usage example" was too vague for a static analyzer and too expensive to enforce in code review. With a sufficiently capable model in the loop, the rule becomes tractable, provided it is written with enough specificity to avoid hallucinations and provided the patcher has the safety rails the README describes. The Rule Report feature treats the rule set itself as a software artifact that can be tested and improved.

## Conclusion

Agentic Gatekeeper is a small, focused tool that addresses a real and under-served problem: the gap between written engineering standards and actually-enforced engineering standards. Its design choices — diff-only context for large files, fuzzy patching, content-and-rule-version caching, automatic rejection of truncation-suspect rewrites, and a multi-provider model abstraction — reflect practical experience with the failure modes of LLM-driven refactoring. The remote-rules feature makes it viable for organization-wide rollout, and the Rule Report feature treats the rule set as an artifact that can be tested. In a 2026 landscape dominated by code generators and autonomous software engineers, a tool that *refuses* to generate and instead chooses to gatekeep is a useful corrective. Turning `CONTRIBUTING.md` from a passive document into active policy is more achievable now than it has ever been, and Agentic Gatekeeper is one of the cleaner implementations of that idea.
