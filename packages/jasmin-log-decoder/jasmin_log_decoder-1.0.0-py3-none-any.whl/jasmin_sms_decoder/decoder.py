#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import re
from datetime import datetime

def decode_content(encoded_str):
    """
    Decode UTF-16BE encoded SMS content from Jasmin logs.

    Args:
        encoded_str: The encoded string to decode

    Returns:
        Decoded string or error message
    """
    try:
        return encoded_str.encode("latin1").decode("unicode_escape").encode("ISO-8859-1").decode("UTF-16BE")
    except Exception as e:
        return f"[DECODING ERROR: {e}]"


def decode_line(line):
    """
    Find and decode content blocks in a log line.

    If decoding fails, keeps original content.

    Args:
        line: A single line from the log file (str)

    Returns:
        Line with decoded content blocks
    """
    def replace_match(match):
        content = match.group(1)
        try:
            decoded = decode_content(content)
            return f"[content:'{decoded}']"
        except Exception:
            # Return original if decoding fails
            return match.group(0)

    # Non-greedy match for multiple content blocks
    return re.sub(r"\[content:b?'(.*?)'\]", replace_match, line)


def process_file_streaming(file, search_term=None):
    """
    Process file line-by-line safely, even if it contains non-UTF8 bytes.

    Args:
        file: Path to the file or file object
        search_term: Optional search filter

    Yields:
        Decoded lines that match the search criteria
    """
    matched_count = 0

    if isinstance(file, str):
        with open(file, "rb") as f:  # read in binary mode
            for line_bytes in f:
                line = line_bytes.decode("latin1").rstrip("\n")
                decoded_line = decode_line(line)

                if search_term:
                    if search_term in decoded_line:
                        matched_count += 1
                        yield decoded_line
                else:
                    matched_count += 1
                    yield decoded_line
    else:
        # Handle file-like object (stdin)
        for line_bytes in file:
            line = line_bytes.decode("latin1").rstrip("\n")
            decoded_line = decode_line(line)

            if search_term:
                if search_term in decoded_line:
                    matched_count += 1
                    yield decoded_line
            else:
                matched_count += 1
                yield decoded_line

    return matched_count


def read_last_n_lines(file, n):
    """
    Read last N lines efficiently using tail.

    Args:
        file: Path to the file
        n: Number of lines to read

    Returns:
        List of lines
    """
    result = subprocess.run(
        ["tail", f"-n{n}", file],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.splitlines()


def log_access(file_path):
    """
    Log access to SMS logs for audit purposes.

    Args:
        file_path: Path to the file being accessed
    """
    audit_log = os.path.expanduser("~/.jasmin_decoder_audit.log")
    try:
        with open(audit_log, "a") as f:
            timestamp = datetime.now().isoformat()
            user = os.getenv("USER", "unknown")
            f.write(f"{timestamp} | User: {user} | File: {file_path}\n")
    except Exception:
        # Silently fail if audit logging fails
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Decode Jasmin SMS Gateway messages from logs",
        epilog="Note: This tool reads SMS content. Ensure proper authorization and compliance."
    )
    parser.add_argument("file", nargs="?", type=str, help="Log file to decode (or use stdin)")
    parser.add_argument("--lines", type=int, help="Only process last N lines (uses tail for efficiency)")
    parser.add_argument("--search", type=str, help="Only show lines containing this decoded text")
    parser.add_argument("--no-audit", action="store_true", help="Disable audit logging")

    args = parser.parse_args()

    # Validate input
    if args.file:
        if not os.path.isfile(args.file):
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)

        if not os.access(args.file, os.R_OK):
            print(f"Error: No read permission for '{args.file}'", file=sys.stderr)
            sys.exit(1)

        # Log access for audit trail (unless disabled)
        if not args.no_audit:
            log_access(args.file)

    # Validate lines count if specified
    if args.lines and args.lines <= 0:
        print("Error: --lines must be a positive integer", file=sys.stderr)
        sys.exit(1)

    matched_count = 0

    try:
        # If --lines specified, use tail for efficiency
        if args.lines:
            if args.file:
                lines = read_last_n_lines(args.file, args.lines)
            else:
                # Read from stdin and take last N lines
                lines = sys.stdin.buffer.read().splitlines()
                # decode with latin1
                lines = [l.decode("latin1") for l in lines[-args.lines:]]

            # Process limited set of lines
            for line in lines:
                decoded_line = decode_line(line)
                if args.search:
                    if args.search in decoded_line:
                        print(decoded_line)
                        matched_count += 1
                else:
                    print(decoded_line)
                    matched_count += 1
        else:
            # Stream processing for entire file (memory efficient)
            if args.file:
                for decoded_line in process_file_streaming(args.file, args.search):
                    print(decoded_line)
                    matched_count += 1
            else:
                for decoded_line in process_file_streaming(sys.stdin.buffer, args.search):
                    print(decoded_line)
                    matched_count += 1

        # Show search results summary if searching
        if args.search and matched_count == 0:
            print(f"No matches found for: '{args.search}'", file=sys.stderr)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except subprocess.CalledProcessError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
