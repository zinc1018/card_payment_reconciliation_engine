# Card Payment Reconciliation Engine

A sanitized Python portfolio scaffold for the card reconciliation tool.

This subproject is intentionally separate from the live Excel/VBA workflow in the repository root. Its purpose is to present the reconciliation logic, data normalization approach, and matching rules in a publishable structure without exposing real payment files.

## Goals

- Preserve the core business rules from the working reconciliation process
- Support both older and newer Global Payments layouts
- Treat Versapay settlement rows as the recon source of truth
- Demonstrate a clean, testable Python architecture for portfolio review

## Current Scope

- Header alias support for:
  - older Global Payments files (`Authorization Code`, `Processing Date`, `Settlement Amount`)
  - newer Global Payments files (`Approval Code`, `Process Date`, `Settled Amount`)
- Versapay normalization with `settle`-only filtering
- Detail reconciliation using:
  - `CardBrand + AuthorizationCode + Amount`
- Derived batch summaries using matched detail rows
- Minimal CLI scaffold for future file-based ingestion

## Project Layout

- `src/card_recon/`
  - Python package for ingest, normalization, matching, and reporting
- `tests/`
  - regression tests for key reconciliation rules
- `samples/`
  - sanitized placeholder data and schema notes only
- `docs/`
  - architecture and rule documentation

## Non-Goals

- This folder does not publish real exports from Versapay or Global Payments.
- This folder does not replace the working Excel/VBA tool yet.
- This folder is not wired to the live workbook.
- This first revision does not yet implement full file ingestion from Excel exports.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
```

Example CLI shape:

```powershell
python -m card_recon.cli --help
```

## Portfolio Framing

This project is best presented as:

`A card payment reconciliation engine that normalizes changing settlement exports, reconciles transaction detail across processors, and derives batch-level reconciliation views from matched records.`
