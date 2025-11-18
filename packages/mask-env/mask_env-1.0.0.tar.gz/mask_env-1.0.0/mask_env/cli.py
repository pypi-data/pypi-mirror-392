"""Command-line interface for mask-env."""

import argparse
import os
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Create safe .env.example files from .env files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mask-env                    # Reads .env, writes .env.example
  mask-env .env              # Reads .env, writes .env.example
  mask-env .env -o output    # Reads .env, writes to output
  mask-env path/.env         # Reads path/.env, writes path/.env.example
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        default='.env',
        help='Input .env file path (default: .env)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output',
        help='Output file path (default: input_path + ".example")'
    )
    
    args = parser.parse_args()
    
    try:
        from mask_env.processor import process_file
        
        secrets_replaced = process_file(args.input, args.output)
        
        output_path = args.output if args.output else args.input + '.example'
        print(f"✓ Created {output_path}")
        print(f"✓ Replaced {secrets_replaced} secret value(s)")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except IsADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Hint: The specified path is a directory, not a file.", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Hint: Check file permissions and ensure you have read/write access.", file=sys.stderr)
        return 1
    except UnicodeDecodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Hint: The file may not be UTF-8 encoded. Please convert it to UTF-8.", file=sys.stderr)
        return 1
    except UnicodeEncodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Hint: Cannot encode data to UTF-8. Check for invalid characters.", file=sys.stderr)
        return 1
    except (ValueError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except MemoryError as e:
        print(f"Error: Out of memory - file may be too large: {e}", file=sys.stderr)
        print("Hint: Try processing a smaller file or increase available memory.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print("Please report this issue if it persists.", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

