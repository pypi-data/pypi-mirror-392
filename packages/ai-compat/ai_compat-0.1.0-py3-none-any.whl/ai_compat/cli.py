"""Command line interface for ai-compat."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .checker import check_compatibility
from .exporter import export_environment
from .fixer import apply_fix_plan, suggest_fixes
from .scanner import scan_system, snapshot_to_dict
from .tester import run_gpu_tests


def cmd_scan(args):
    snapshot = scan_system()
    print(json.dumps(snapshot_to_dict(snapshot), indent=2))


def cmd_check(args):
    snapshot = scan_system()
    report = check_compatibility(snapshot)
    print(json.dumps(report.to_dict(), indent=2))


def cmd_fix(args):
    snapshot = scan_system()
    report = check_compatibility(snapshot)
    plans = suggest_fixes(report)
    if not plans:
        print("No fixes required")
        return
    for plan in plans:
        print(f"Issue: {plan.issue.message}")
        for action in plan.actions:
            print(f" - {action.description}: {' '.join(action.command) if action.command else 'manual action required'}")
            if args.apply and action.command:
                apply_fix_plan(plan, dry_run=False)
                break


def cmd_test(args):
    results = run_gpu_tests()
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.name}: {result.message}")


def cmd_export(args):
    snapshot = scan_system()
    output = export_environment(snapshot, Path(args.output))
    print(f"Environment file written to {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI GPU compatibility toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scan", help="Scan system info").set_defaults(func=cmd_scan)
    sub.add_parser("check", help="Check compatibility").set_defaults(func=cmd_check)

    fix_parser = sub.add_parser("fix", help="Suggest or apply fixes")
    fix_parser.add_argument("--apply", action="store_true", help="Apply fixes using pip")
    fix_parser.set_defaults(func=cmd_fix)

    sub.add_parser("test", help="Run GPU diagnostics").set_defaults(func=cmd_test)

    export_parser = sub.add_parser("export", help="Export environment file")
    export_parser.add_argument("--output", default="gpu-env.txt", help="Output file")
    export_parser.set_defaults(func=cmd_export)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
