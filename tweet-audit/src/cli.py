# the cli module that handles user interaction with the application

import argparse

from config import setup_logger

from src.service import AuditService

import sys
logger = setup_logger(__name__, "cli.log")


def main():
    parser = argparse.ArgumentParser(
        description="a command line service to handle extraction and analysis of X tweets from archives",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["extract-tweets", "analyze-tweets"],
        help="Command to execute",
    )
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    app = AuditService()
    if args.command == "extract-tweets":
        logger.info("Starting tweet extraction")
        data = app.extract_tweets()
        if not data.success:
            logger.error(f"Extraction failed: {data.error_message}")
            print(f"Error occurred: {data.error_message}")
            sys.exit(1)
        else:
            logger.info(f"Successfully extracted {data.count} tweets")
            print(f"Successfully extracted: {data.count}")

    elif args.command == "analyze-tweets":
        logger.info("Starting tweet analysis")
        data = app.analyze_tweets()
        if not data.success:
            logger.error(f"Analysis failed: {data.error_message}")
            print(f"An error occurred: {data.error_message}")
            sys.exit(1)
        else:
            logger.info(f"Successfully analyzed {data.count} tweets")
            print(f"Successfully analyzed: {data.count} tweets")


if __name__ == "__main__":
    main()
