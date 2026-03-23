from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="card_recon",
        description="Sanitized card payment reconciliation engine",
    )
    parser.add_argument("--versapay", help="Path to a Versapay export")
    parser.add_argument("--gp", help="Path to a Global Payments export")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate arguments and print planned processing only",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.dry_run:
        print("Dry run mode")
        print(f"Versapay: {args.versapay or '(not provided)'}")
        print(f"Global Payments: {args.gp or '(not provided)'}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
