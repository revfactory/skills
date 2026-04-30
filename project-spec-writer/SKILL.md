---
name: project-spec-writer
description: Write comprehensive XML-structured project specifications for software projects. Use when a user wants to create a build plan, project spec, technical specification, or detailed requirements document for an application they want built. Triggers include requests like "write a project spec", "create a build plan", "make a technical specification", "spec out this app idea", "write requirements for my project", or any request to produce a structured document describing what to build. Also use when refining or expanding an existing spec. The output is an XML-formatted .md file optimized for consumption by AI coding agents (e.g., Claude Code, Cursor, Copilot Workspace) or human developers.
---

# Project Specification Writer

Generate detailed, structured XML project specifications that serve as comprehensive build plans for software projects. The specs are designed to be consumed by AI coding agents or developers to build applications with minimal ambiguity.

## Workflow

### 1. Gather Project Intent

Ask the user about their project. Prioritize understanding:

1. **What** — Core purpose and key features (e.g., "a JIRA-like project management app")
2. **How** — Technical preferences: framework, language, hosting model (e.g., "React + IndexedDB, no backend")
3. **Who** — Target users and usage context
4. **Look & Feel** — Design preferences, reference apps, color themes

If the user provides a brief idea, ask focused follow-up questions (max 2-3 per message) to fill gaps. If the user provides a detailed brief, proceed directly.

For **technology stack**, suggest sensible defaults if the user has no preference. Default toward modern, well-documented tools: React/Vite for web apps, Tailwind for styling, TypeScript for type safety.

### 2. Draft the Specification

Read the XML schema reference: [references/xml-schema.md](references/xml-schema.md)

Write the specification inside a single `<project_specification>` root tag. Follow this section order:

```
project_name → overview → scope_boundaries →
technology_stack → prerequisites → environment_variables → file_structure →
core_data_entities → authentication → route_definitions → component_hierarchy →
pages_and_interfaces → core_functionality → error_handling →
third_party_integrations → aesthetic_guidelines → security_considerations →
advanced_functionality → final_integration_test → success_criteria →
build_output → key_implementation_notes
```

Skip sections that don't apply to the project type (see applicability table in schema reference). For a complete example spec, see [references/example-spec.md](references/example-spec.md).

#### Writing Principles

**Be concrete, not abstract.** Every design decision should have a specific value:
- Colors: hex codes (`#1B4332`), not names ("dark green")
- Dimensions: pixel values (`56px`), not vague sizes ("large")
- Libraries: name + version (`Recharts v3.5`), not categories ("a charting library")
- Enums: list all values (`enum (Story, Bug, Task, Epic, Sub-task)`)

**Be exhaustive on data models.** Every entity needs complete field definitions with types, constraints, and relationships. Include compound indexes for any non-trivial querying patterns.

**Be specific on UI.** For each view/page, specify: layout structure, dimensions, colors, content hierarchy, interactive behaviors (hover/click/drag/keyboard), empty states, and animations with durations.

**Be opinionated on design.** Provide a complete design system: color palette (primary, background, text, status, semantic groups), typography (families with fallbacks, size scale), spacing system (base unit + scale), component styles (buttons, inputs, cards, etc.), animation specifications.

**Be actionable on implementation.** Include a recommended implementation order that respects dependency chains. Provide concrete code for schemas/configs where helpful. List critical paths that need early attention.

**Write for AI agents.** The spec consumer may be an AI coding agent. Prefer explicit, unambiguous descriptions. State architectural constraints with `CRITICAL:` prefix. Avoid prose that requires interpretation — use structured lists and specific values.

### 3. Output Format

Save as a `.md` file with the XML content. The filename should be the project name in SCREAMING_SNAKE_CASE with `_SPEC` suffix:
- `CANOPY_SPEC.md`
- `RECIPE_TRACKER_SPEC.md`

For large specs (>500 lines), write iteratively: outline first, then fill sections one at a time.

### 4. Review and Refine

After drafting, verify against the quality checklist in the schema reference. Common gaps:
- Missing empty states for views
- Missing keyboard shortcuts
- Vague success criteria (add numbers)
- Incomplete data entity fields
- Missing dark theme colors (if theme switching is specified)
- Missing animation durations/easings
- Missing scope boundaries (what this project is NOT)
- Missing file structure tree
- Missing component hierarchy / provider wrapping order
- Missing responsive breakpoints and mobile adaptations
- Missing error handling patterns (toasts, form validation, error pages)
- Missing security considerations (input validation, CORS, rate limits)
- Missing environment variables list

Present the spec to the user and offer to expand, revise, or add detail to any section.

## Section Depth Guidelines

Match detail level to project complexity:

| Project Complexity | Spec Length | Data Entities | UI Pages | Test Scenarios |
|-------------------|-------------|---------------|----------|----------------|
| Simple (todo, timer) | 200-400 lines | 2-4 entities | 2-4 views | 3-5 scenarios |
| Medium (blog, dashboard) | 400-800 lines | 5-8 entities | 5-10 views | 6-8 scenarios |
| Complex (PM tool, CRM) | 800-1700 lines | 8-15 entities | 10-20 views | 10-15 scenarios |

## Adaptation for Non-Web Projects

For API/backend projects: Replace `pages_and_interfaces` with `<api_endpoints>` listing routes, methods, request/response schemas, auth requirements, and error codes.

For CLI tools: Replace `pages_and_interfaces` with `<commands_and_flags>` listing commands, arguments, flags, output formats, and interactive prompts. Replace `aesthetic_guidelines` with `<output_formatting>` for terminal output styling.

For libraries/SDKs: Replace `pages_and_interfaces` with `<public_api>` listing exported functions, classes, types, and usage examples. Replace `aesthetic_guidelines` with `<api_design_principles>`.
