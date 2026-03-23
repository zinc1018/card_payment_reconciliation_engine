# Architecture

## Intent

This Python subproject is the publishable version of the reconciliation logic. It keeps the business rules and drops operational coupling to a live Excel workbook.

## Core Rules

- Versapay reconciliation uses `settle` rows only.
- Global Payments supports multiple header layouts through aliases.
- Global Payments adjustment rows are excluded before reconciliation.
- Detail matching is based on:
  - `CardBrand`
  - `AuthorizationCode`
  - `Amount`
- Batch reconciliation is derived from matched detail rows instead of assuming Global Payments batch control equals Versapay batch id.

## Modules

- `schemas.py`
  - logical field aliases per source system
- `models.py`
  - normalized record structures
- `normalize.py`
  - raw row to normalized record conversion
- `match.py`
  - detail matching and batch rollup
- `report.py`
  - simple serializable outputs
- `cli.py`
  - command-line entry point

## Why This Structure

- Easier to test than VBA
- Easier to explain in a portfolio
- Easier to extend into CLI, API, or web tooling
