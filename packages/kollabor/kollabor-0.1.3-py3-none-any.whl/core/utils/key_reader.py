#!/usr/bin/env python3
"""Key reader utility for debugging terminal input sequences.

This tool helps debug what actual key sequences are sent by the terminal
when pressing various key combinations. Useful for implementing new
keyboard shortcuts and understanding terminal behavior.

Usage:
    python core/utils/key_reader.py

Press keys to see their sequences, Ctrl+C to exit.
"""

import sys
import tty
import termios
import signal

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\n\nExiting key reader...')
    sys.exit(0)

def main():
    """Main key reader loop."""
    print("Key Reader - Press keys to see their sequences (Ctrl+C to exit)")
    print("=" * 60)

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)

    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        # Set terminal to raw mode
        tty.setraw(sys.stdin.fileno())

        key_count = 0

        while True:
            # Read one character
            char = sys.stdin.read(1)
            key_count += 1

            # Get character info
            ascii_code = ord(char)
            hex_code = hex(ascii_code)

            # Determine key name
            if ascii_code == 3:  # Ctrl+C
                print(f"\n\r[{key_count:03d}] Key: 'CTRL+C' | ASCII: {ascii_code} | Hex: {hex_code} | Raw: {repr(char)}")
                break
            elif ascii_code == 27:  # ESC or start of escape sequence
                key_name = "ESC"
                # Try to read more characters for escape sequences
                try:
                    # Set a short timeout to see if more chars follow
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        sequence = char
                        while select.select([sys.stdin], [], [], 0.05)[0]:
                            next_char = sys.stdin.read(1)
                            sequence += next_char
                            if len(sequence) > 10:  # Prevent infinite sequences
                                break

                        # Update display info
                        char = sequence
                        ascii_code = f"ESC sequence"
                        hex_code = " ".join(hex(ord(c)) for c in sequence)
                        key_name = f"ESC_SEQ({sequence[1:]})" if len(sequence) > 1 else "ESC"
                except:
                    pass
            elif 1 <= ascii_code <= 26:  # Ctrl+A through Ctrl+Z
                key_name = f"CTRL+{chr(ascii_code + 64)}"
            elif ascii_code == 127:
                key_name = "BACKSPACE"
            elif 32 <= ascii_code <= 126:
                key_name = f"'{char}'"
            else:
                key_name = f"SPECIAL({ascii_code})"

            # Display the key info
            print(f"\r[{key_count:03d}] Key: {key_name} | ASCII: {ascii_code} | Hex: {hex_code} | Raw: {repr(char)}")

    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()