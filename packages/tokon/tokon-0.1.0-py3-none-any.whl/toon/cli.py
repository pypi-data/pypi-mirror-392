#!/usr/bin/env python3
import sys
import json
import argparse
from typing import Optional
from . import encode, decode, TOONEncodeError, TOONDecodeError

def main():
    parser = argparse.ArgumentParser(
        description="TOON (Token-Oriented Object Notation) encoder/decoder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode JSON to TOON
  echo '{"name": "Alice", "age": 30}' | tokon encode
  
  # Decode TOON to JSON
  echo 'name: Alice\\nage: 30' | tokon decode
  
  # Encode with tab delimiter
  echo '{"items": [{"id": 1}]}' | tokon encode --delimiter tab
  
  # Decode from file
  tokon decode < data.toon
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    encode_parser = subparsers.add_parser("encode", help="Encode JSON to TOON")
    encode_parser.add_argument(
        "--delimiter",
        choices=["comma", "tab", "pipe"],
        default="comma",
        help="Delimiter to use (default: comma)"
    )
    encode_parser.add_argument(
        "--input",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file (default: stdin)"
    )
    encode_parser.add_argument(
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file (default: stdout)"
    )
    
    decode_parser = subparsers.add_parser("decode", help="Decode TOON to JSON")
    decode_parser.add_argument(
        "--delimiter",
        choices=["comma", "tab", "pipe"],
        help="Delimiter to use (auto-detected if not specified)"
    )
    decode_parser.add_argument(
        "--input",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file (default: stdin)"
    )
    decode_parser.add_argument(
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file (default: stdout)"
    )
    decode_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    delimiter_map = {
        "comma": ",",
        "tab": "\t",
        "pipe": "|"
    }
    
    try:
        if args.command == "encode":
            input_data = args.input.read()
            if not input_data.strip():
                print("Error: No input data provided", file=sys.stderr)
                sys.exit(1)
            
            try:
                json_data = json.loads(input_data)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
                sys.exit(1)
            
            delimiter = delimiter_map[args.delimiter]
            toon_output = encode(json_data, delimiter=delimiter)
            args.output.write(toon_output)
            if not toon_output.endswith("\n"):
                args.output.write("\n")
        
        elif args.command == "decode":
            input_data = args.input.read()
            if not input_data.strip():
                print("Error: No input data provided", file=sys.stderr)
                sys.exit(1)
            
            delimiter = delimiter_map.get(args.delimiter) if args.delimiter else None
            try:
                decoded_data = decode(input_data, delimiter=delimiter)
            except TOONDecodeError as e:
                print(f"Error: Failed to decode TOON: {e}", file=sys.stderr)
                sys.exit(1)
            
            json_output = json.dumps(
                decoded_data,
                indent=2 if args.pretty else None,
                separators=(",", ":") if not args.pretty else None,
                ensure_ascii=False
            )
            args.output.write(json_output)
            if not json_output.endswith("\n"):
                args.output.write("\n")
    
    except TOONEncodeError as e:
        print(f"Error: Failed to encode: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

