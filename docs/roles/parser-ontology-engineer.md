# Parser and ontology engineer

## Mission
- Convert source agent configs into a neutral, ordered intermediate representation with a stable
  concept ontology.

## Scope
- Markdown/AST parsing for headings, lists, code fences, inline directives, and comments.
- Kiro-specific folder parsing, file intent classification, and merge rules.
- Ontology definition: categories, required vs optional concepts, versioning, ambiguity handling.
- Preservation of raw text while tagging sections with semantic labels.

## Outputs
- Parser module that keeps original ordering and groups multi-file configs into a single IR.
- Ontology definitions and helpers that map sections to concepts with warnings on gaps.
- Tests for ambiguous sections, unrecognized content, Kiro merges, and order preservation.
- Warnings surfaced to mapping/renderer layers when data is missing or unsupported.

## Inputs needed
- Registry signals about known file patterns and agent constraints.
- Mapping requirements about the granularity of concepts and expected fallbacks.
- Streaming requirements when emitting parsed sections downstream.

## Collaboration signals
- Pair with mapping engineer on ontology coverage and downgrade paths.
- Pair with renderer engineer on which fields must be preserved verbatim.
- Loop QA on snapshot fixtures and ambiguity edge cases.

## Risks to watch
- Losing contextual ordering when normalizing sections.
- Over-normalizing and erasing raw instructions needed for target agents.
- Kiro folder heuristics misclassifying files with similar names.
