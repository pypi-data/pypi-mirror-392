"""CLI entry point for AgenticlyPay."""

import sys
import argparse
from agenticlypay.config import config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AgenticlyPay CLI")
    parser.add_argument(
        "--version", action="version", version="AgenticlyPay 0.1.0"
    )
    parser.add_argument(
        "--config", action="store_true", help="Show current configuration"
    )

    args = parser.parse_args()

    if args.config:
        print("AgenticlyPay Configuration:")
        print(f"  Platform: {config.platform_name}")
        print(f"  Fee: {config.platform_fee_percentage * 100}% + ${config.platform_fee_fixed / 100}")
        print(f"  API Host: {config.api_host}")
        print(f"  API Port: {config.api_port}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

