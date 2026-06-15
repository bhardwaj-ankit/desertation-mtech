"""
Data preparation package for the Agentic Multimodal AI Techlog Intelligence project.

This package builds the datasets required by the dissertation prototype:

  * Synthetic aircraft techlogs (defect narratives + structured metadata)
  * FAA SDR-style structured defect records
  * A RAG knowledge corpus (AMM manual snippets, MEL/CDL, Airworthiness
    Directives, engineering orders, operational advisories, prior cases)
  * C-MAPSS-style multivariate operational signal windows mapped to defects
  * QA pairs for grounded-RAG evaluation (can-answer / must-cite / must-abstain)
  * Train/val/test splits for triage, recurrence and multimodal experiments

Everything is generated with the Python standard library only (no pandas /
numpy required) so the groundwork runs reliably on any machine. Outputs are
written as CSV / JSON / JSONL which downstream pandas / torch code can read.

See ``data/DATA_CARD.md`` for provenance, schema and licensing notes.
"""

__all__ = ["taxonomy"]
