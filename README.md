import argparse
import sys

def validate_arguments(args):
    """
    Validates that either the intake file is provided or the API arguments are all provided.
    """
    if args.intake_file:
        # If the intake file is provided, no API arguments should be provided
        if args.api_base or args.api_user or args.api_password:
            raise argparse.ArgumentError(None, "If -f/--intake-file is provided, -a/--api-base, -u/--api-user, and -p/--api-password should not be provided.")
    else:
        # If the intake file is not provided, all API arguments are required
        if not (args.api_base and args.api_user and args.api_password):
            raise argparse.ArgumentError(None, "If -f/--intake-file is not provided, all of -a/--api-base, -u/--api-user, and -p/--api-password are required.")

def main():
    parser = argparse.ArgumentParser(description="Process intake file or use API credentials.")

    # Intake file argument
    parser.add_argument("-f", "--intake-file", help="Path to the intake file")

    # API arguments
    parser.add_argument("-a", "--api-base", help="Base URL for the API")
    parser.add_argument("-u", "--api-user", help="Username for the API")
    parser.add_argument("-p", "--api-password", help="Password for the API")

    args = parser.parse_args()

    try:
        validate_arguments(args)
    except argparse.ArgumentError as e:
        parser.error(str(e))
        sys.exit(1)

    # If validation passes, you can proceed with your program logic
    if args.intake_file:
        print(f"Using intake file: {args.intake_file}")
    else:
        print(f"Using API with base URL: {args.api_base}, user: {args.api_user}")

if __name__ == "__main__":
    main()