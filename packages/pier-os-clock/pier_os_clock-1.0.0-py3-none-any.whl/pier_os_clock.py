#!/usr/bin/env python3
"""
pier-os-clock - Minimal terminal clock tool for Linux/WSL

Copyright 2024 Dogukan Sahil

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import time
import signal
from datetime import datetime


def clear_screen():
    """Clear the terminal screen using ANSI escape sequences."""
    sys.stdout.write('\033[2J')  # Clear entire screen
    sys.stdout.write('\033[H')   # Move cursor to home position
    sys.stdout.flush()


def get_terminal_size():
    """
    Get terminal dimensions (columns, rows).
    
    Returns:
        tuple: (columns, rows) tuple with terminal dimensions.
               Defaults to (80, 24) if unable to determine size.
    """
    try:
        import shutil
        size = shutil.get_terminal_size()
        return (size.columns, size.lines)
    except (AttributeError, OSError):
        return (80, 24)  # Default fallback dimensions


def center_text(text, width):
    """
    Center text horizontally within given width.
    
    Args:
        text (str): Text to center.
        width (int): Total width for centering.
    
    Returns:
        str: Centered text string.
    """
    return text.center(width)


def display_clock():
    """
    Main clock display loop.
    
    Continuously displays the current time centered on screen,
    updating every second. Handles KeyboardInterrupt gracefully.
    """
    try:
        while True:
            clear_screen()
            cols, rows = get_terminal_size()
            
            # Get current time in HH:MM:SS format
            now = datetime.now()
            time_str = now.strftime('%H:%M:%S')
            
            # Calculate vertical centering
            vertical_padding = (rows - 1) // 2
            centered_time = center_text(time_str, cols)
            
            # Print empty lines for vertical centering
            for _ in range(vertical_padding):
                print()
            
            # Print centered time
            print(centered_time, end='', flush=True)
            
            # Wait for next second
            time.sleep(1)
            
    except KeyboardInterrupt:
        clear_screen()
        sys.exit(0)


def signal_handler(sig, frame):
    """
    Handle interrupt signals gracefully.
    
    Args:
        sig: Signal number.
        frame: Current stack frame.
    """
    clear_screen()
    sys.exit(0)


def main():
    """
    Main entry point for the application.
    
    Registers signal handlers and starts the clock display loop.
    Exits with error code if not running in a terminal.
    """
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Verify we're running in a terminal
    if not sys.stdout.isatty():
        print("Error: This program must be run in a terminal.", file=sys.stderr)
        sys.exit(1)
    
    display_clock()


if __name__ == '__main__':
    main()
