#!/usr/bin/env python3
"""
Tokon CLI Tool

Command-line interface for encoding and decoding Tokon format.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from . import encode, decode, load_schema, TokonEncodeError, TokonDecodeError


def main():
    parser = argparse.ArgumentParser(
        description="Tokon v1.1 - Token-Optimized Serialization Format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode JSON to Tokon-H
  echo '{"name": "Alice", "age": 30}' | tokon encode -m h
  
  # Encode to Tokon-C with schema
  echo '{"name": "Alice", "age": 30}' | tokon encode -m c -s user.tks
  
  # Decode Tokon to JSON
  echo 'name Alice\\nage 30' | tokon decode
  
  # Auto-detect mode
  cat data.tokon | tokon decode
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    encode_parser = subparsers.add_parser("encode", help="Encode JSON to Tokon")
    encode_parser.add_argument(
        "-m", "--mode",
        choices=["h", "c"],
        default="h",
        help="Output mode: 'h' for human-readable, 'c' for compact (default: h)"
    )
    encode_parser.add_argument(
        "-s", "--schema",
        type=str,
        help="Schema file path (.tks)"
    )
    encode_parser.add_argument(
        "-i", "--input",
        type=argparse.FileType('r', encoding='utf-8'),
        default=sys.stdin,
        help="Input JSON file (default: stdin)"
    )
    encode_parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('w', encoding='utf-8'),
        default=sys.stdout,
        help="Output Tokon file (default: stdout)"
    )
    
    decode_parser = subparsers.add_parser("decode", help="Decode Tokon to JSON")
    decode_parser.add_argument(
        "-m", "--mode",
        choices=["h", "c", "auto"],
        default="auto",
        help="Input mode: 'h', 'c', or 'auto' (default: auto)"
    )
    decode_parser.add_argument(
        "-s", "--schema",
        type=str,
        help="Schema file path (.tks)"
    )
    decode_parser.add_argument(
        "-i", "--input",
        type=argparse.FileType('r', encoding='utf-8'),
        default=sys.stdin,
        help="Input Tokon file (default: stdin)"
    )
    decode_parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('w', encoding='utf-8'),
        default=sys.stdout,
        help="Output JSON file (default: stdout)"
    )
    decode_parser.add_argument(
        "-p", "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )
    
    args = parser.parse_args()
    
    if args.command == "encode":
        try:
            input_data = args.input.read()
            if not input_data.strip():
                raise TokonEncodeError("Empty input for encoding")
            
            json_data = json.loads(input_data)
            
            schema = None
            if args.schema:
                schema_path = Path(args.schema)
                if not schema_path.exists():
                    print(f"Error: Schema file not found: {args.schema}", file=sys.stderr)
                    sys.exit(1)
                schema = load_schema(schema_path)
            
            toon_output = encode(json_data, mode=args.mode, schema=schema)
            args.output.write(toon_output)
            if args.output.isatty():
                args.output.write("\n")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
        except TokonEncodeError as e:
            print(f"Error encoding to Tokon: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "decode":
        try:
            input_data = args.input.read()
            if not input_data.strip():
                raise TokonDecodeError("Empty input for decoding")
            
            schema = None
            if args.schema:
                schema_path = Path(args.schema)
                if not schema_path.exists():
                    print(f"Error: Schema file not found: {args.schema}", file=sys.stderr)
                    sys.exit(1)
                schema = load_schema(schema_path)
            
            decoded_data = decode(input_data, mode=args.mode, schema=schema)
            
            if args.pretty:
                json.dump(decoded_data, args.output, indent=2)
            else:
                json.dump(decoded_data, args.output, separators=(',', ':'))
            
            if args.output.isatty():
                args.output.write("\n")
        except TokonDecodeError as e:
            print(f"Error decoding Tokon: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

