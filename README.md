# Backend Ops Agent Lab

A local-first laboratory for learning agentic systems in a backend operations context.

This project explores how to build a small, testable agent that can combine:
- incident data,
- operational documentation,
- local model inference,
- and simple orchestration logic

to produce an initial backend operations diagnosis.

The focus of this lab is not autonomy for its own sake.  
The focus is to learn the foundations of agentic systems through a concrete and engineering-oriented use case.

## Goals

- Learn the core building blocks of an agentic system
- Keep the lab local-first and low-cost
- Start with a small vertical slice instead of a broad platform
- Separate domain logic from infrastructure concerns
- Build a codebase that is easy to test, refactor, and evolve

## Current Architecture

The initial lab includes:

- **agent-app**  
  Main Python application responsible for orchestrating the investigation flow

- **mock-api**  
  Small backend API used to simulate incident data

- **Ollama**  
  Local model runtime used for chat/inference

- **Qdrant**  
  Local vector database for document retrieval experiments

- **Docker Compose**  
  Local orchestration for the full lab environment

## Project Structure

```text
.
├── docker-compose.yml
├── .env.example
├── docs/
│   └── runbooks/
├── services/
│   ├── agent-app/
│   └── mock-api/
├── scripts/
└── README.md
```

## Development Scripts

The repository currently includes two PowerShell scripts for local development on Windows:

- **`scripts/dev-up.ps1`**  
  Starts the local development environment using Docker Compose.  
  It can optionally rebuild images, run the environment in detached mode, and pull the default Ollama model.

  Example usage:

  ```powershell
  .\scripts\dev-up.ps1
  .\scripts\dev-up.ps1 -Build
  .\scripts\dev-up.ps1 -Detached
  .\scripts\dev-up.ps1 -Build -Detached -PullModel
  ```

- **`scripts/smoke-test.ps1`**  
  Runs a quick end-to-end smoke test against the local environment.  
  It checks service health and calls the `/investigate` endpoint with a default incident id.

  Example usage:

  ```powershell
  .\scripts\smoke-test.ps1
  .\scripts\smoke-test.ps1 -IncidentId INC-002
  ```

Recommended workflow:

1. Start the environment with `dev-up.ps1`
2. Validate it with `smoke-test.ps1`

## Engineering Principles

This lab starts from a few explicit engineering principles:

- **Small end-to-end slices first**  
  Inspired by *The Pragmatic Programmer*: build a working vertical slice early.

- **Domain logic separated from infrastructure**  
  Inspired by *Clean Architecture*: keep the core use case independent from Ollama, Qdrant, and HTTP details.

- **Refactor-friendly structure**  
  Inspired by *Refactoring*: expect the design to evolve as the lab grows.

- **Simple, testable interfaces**  
  Inspired by *Code Complete* and *Working Effectively with Legacy Code*: isolate external dependencies behind ports/adapters.

- **Behavior-first tests**  
  Inspired by *TDD by Example*: test the use case and tool contracts early.

- **Professional discipline over cleverness**  
  Inspired by *The Clean Coder*: prioritize clarity, repeatability, and maintainability.