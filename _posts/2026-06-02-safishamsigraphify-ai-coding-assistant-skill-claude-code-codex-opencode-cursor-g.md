---
layout: post
title: "Graphify: Turning Codebases, Schemas, and Documentation into a Queryable Knowledge Graph for AI Coding Assistants"
subtitle: ""
banner:
  image: /assets/images/posts/20260602080040-bb01f192.jpg
  opacity: 0.7
author: zane.deng
categories: [AI Coding]
tags:
- AI Coding
- Translation
- github
---

## The Context Problem in AI-Assisted Software Engineering

Large language models have rapidly become fixtures of the modern software development workflow, powering coding assistants such as Claude Code, OpenAI Codex, Cursor, OpenCode, and the Gemini CLI. Despite their fluency, these assistants share a structural weakness: their effectiveness is bounded by what they can *see* at inference time. A model's context window — even when augmented with retrieval — is fundamentally a flat, lossy projection of a codebase. Conventional retrieval-augmented generation (RAG) pipelines chunk documents into text fragments, embed them into a vector space, and surface the top-k nearest neighbors to a query. This approach is reasonable for prose, but it systematically underperforms when the relevant knowledge is *relational*: a function that calls a stored procedure, a migration that depends on a schema, a Terraform module that provisions the table a microservice reads from. The dependency lives in the *graph*, not in any individual chunk.

The result is a familiar failure mode. An assistant that has read every Python file in a repository can still hallucinate the name of a column, miss a foreign-key constraint, or rewrite a query against a table that does not exist in production. The information is, in some sense, "in the codebase" — but it is not *retrievable* through the mechanisms the assistant has been given.

## Introducing Graphify

Graphify, the open-source project by safishamsi that has accumulated roughly 58,000 stars on GitHub, is a skill — in the sense of a reusable, attachable capability — for AI coding assistants that addresses this gap by turning any folder of heterogeneous content into a **queryable knowledge graph**. Where a typical coding-assistant integration ingests a directory of files and produces a flat index, Graphify parses the contents, extracts entities and relations, and materializes them as a traversable graph. The assistant can then issue graph queries — "which services read from `orders`?", "what is the call graph of the billing cron?", "which Terraform resources back this Lambda?" — and receive precise, structurally grounded answers.

The skill is designed to be **content-agnostic**. It accepts source code in arbitrary languages, SQL schemas, R scripts, shell scripts, documentation, academic papers, images, and videos as first-class inputs. Each artifact type is parsed through an appropriate extractor: parsers for popular programming languages yield abstract syntax trees, SQL dumps yield schema and constraint graphs, scripts yield call and dependency edges, and unstructured media are summarized and linked to the entities they reference. The output is a single, unified graph in which an application's code, its database schema, and its infrastructure all coexist as nodes and edges of the same type system.

## How Ingestion Becomes a Graph

The transformation from "folder of files" to "queryable graph" proceeds in three logical stages. First, each input is routed to a type-appropriate **extractor**: AST-based parsers for general-purpose languages, schema-aware parsers for SQL DDL and migration files, lightweight interpreters for shell and R scripts, and document parsers — including OCR and speech transcription for images and videos — for unstructured media. Second, the extractor emits a stream of **entities** (functions, classes, tables, columns, modules, resources, papers, figures) and **relations** (calls, reads, writes, depends-on, defined-in, cited-by, depicted-in). Third, the streams are merged into a single graph store with stable identifiers, so that the same column referenced from Python, SQL, and a Terraform `aws_dynamodb_table` resource collapses into one node with three incoming edges.

The result is a representation in which traversal replaces similarity search. An assistant no longer asks "which chunks mention `orders.created_at`?"; it asks "what is the impact set of `orders.created_at`?" and follows edges deterministically.

## Why Unify Code, Schema, and Infrastructure?

Modern software systems are polyglot and poly-store by construction. A typical web application is composed of a frontend bundle, one or more backend services written in a general-purpose language, an analytics layer in R or Python, a relational database whose schema evolves through migrations, and infrastructure defined in Terraform, CloudFormation, or shell scripts. Each of these layers carries part of the system's specification. No single layer is sufficient on its own: a column rename is a code change, a schema change, *and* potentially a downstream reporting change in R.

By unifying all three layers in one graph, Graphify enables a class of queries that are simply impossible with text-retrieval. An assistant can ask: "for every endpoint that calls `user.email`, what is the column's type, and which reports join on it?" The graph traversal — endpoint → service function → SQL query → column → reporting R script — is deterministic, reproducible, and inspectable. Errors of the "the model forgot a layer" variety become structurally unrepresentable.

## Supported Platforms and Integration

Graphify is delivered as a portable skill that integrates with the major AI coding environments in use today. Out of the box, it works with **Claude Code**, **OpenAI Codex**, **OpenCode**, **Cursor**, and the **Gemini CLI**, and its design is open to additional adapters as the ecosystem grows. From the assistant's perspective, installation is a matter of registering the skill; from the developer's perspective, it surfaces as additional commands and tools the assistant can invoke to traverse the graph during a session. Because the graph is the contract, the same set of structural queries can be issued from any supported host, and the answers do not change with the model.

## Practical Use Cases

### Onboarding and Code Comprehension

A new engineer — or a new assistant session — can ask structural questions and receive precise answers: "what writes to this table?", "what depends on this module?", "where is this constant defined and where is it consumed?" The graph serves as an executable, always-up-to-date map of the system.

### Safe Refactoring Across Layers

Renaming a column, splitting a service, or migrating from one queue to another is a *graph* operation. With Graphify, the assistant can enumerate the full impact set — every code path, every migration, every dashboard — before proposing a change, dramatically reducing the surface area for subtle bugs.

### Incident Response and Postmortems

When a service degrades, the relevant facts are usually scattered: a metric, a recent deployment, a schema migration, a configuration change. A graph that ties all four together lets the assistant reason about correlations a human operator might not notice in the time available.

### Documentation Synthesis

Because papers, design documents, and images are also ingested, the graph doubles as a knowledge-management substrate. The assistant can answer "what does the system do?" by traversing from code outward into prose, rather than guessing from variable names.

## Value Proposition for AI Coding Assistants

The deeper argument for Graphify is that the relationships that matter in software are exactly the relationships a knowledge graph is designed to capture. Vector retrieval optimizes for *semantic proximity*; software engineering demands *structural fidelity*. By giving an assistant a graph rather than a haystack, the failure modes of chunk-based RAG — the missed foreign key, the hallucinated column name, the unobserved migration — are replaced by deterministic, inspectable traversals. The assistant's role shifts from "text predictor with access to snippets" to "reasoning agent with structural memory," and that shift is the project's central contribution to the AI coding stack.

## Conclusion

Graphify represents a pragmatic step toward treating a software project as a first-class knowledge artifact rather than a directory of files. By converting heterogeneous inputs — code, SQL, scripts, docs, media — into a single queryable graph, and by exposing that graph to the major AI coding assistants, it reframes what "context" means for an AI engineer. For teams that have felt the ceiling of vector-based RAG, the appeal is straightforward: the relationships that matter in software are exactly the relationships a knowledge graph is designed to capture.
