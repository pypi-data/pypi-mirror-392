#!/usr/bin/env python3
"""Main CLI entry point for Gemini CLI."""

import os
import sys
import re
import argparse
from dotenv import load_dotenv
import google.generativeai as genai
from colorama import init, Fore, Style, Back

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Load environment variables
load_dotenv()

# Hardcoded API key (same as Node.js version)
API_KEY = "AIzaSyCxKLAzM8tV51bWptnJCPCj8JysBgu1b6Y"

# Model mapping
MODEL_MAP = {
    "flash": {"name": "gemini-2.5-flash", "display": "⚡ Gemini 2.5 Flash"},
    "2.0-flash": {"name": "gemini-2.0-flash", "display": "⚡ Gemini 2.0 Flash"},
    "2.5-pro": {"name": "gemini-2.5-pro", "display": "🟦 Gemini 2.5 Pro"},
    "1.5-pro": {"name": "gemini-pro-latest", "display": "🟦 Gemini Pro Latest"},
    "pro-latest": {"name": "gemini-pro-latest", "display": "🟦 Gemini Pro Latest"},
    "pro@latest": {"name": "gemini-pro-latest", "display": "🟦 Gemini Pro Latest"},
}


def format_response(text):
    """Format the response text with beautiful styling."""
    lines = text.split("\n")
    formatted_lines = []
    in_code_block = False
    code_block_lines = []
    code_block_lang = ""

    for line in lines:
        # Detect code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                # End of code block
                formatted_lines.append("")
                max_code_width = 76
                formatted_lines.append(
                    Back.BLACK + Fore.WHITE + " ┌" + "─" * max_code_width + "┐"
                )
                for code_line in code_block_lines:
                    # Handle long lines by wrapping
                    if len(code_line) > max_code_width:
                        for j in range(0, len(code_line), max_code_width):
                            chunk = code_line[j : j + max_code_width]
                            padded = chunk.ljust(max_code_width)
                            formatted_lines.append(
                                Back.BLACK
                                + Fore.WHITE
                                + " │"
                                + Back.WHITE
                                + Fore.BLACK
                                + " "
                                + padded
                                + " "
                                + Back.BLACK
                                + Fore.WHITE
                                + "│"
                            )
                    else:
                        padded = code_line.ljust(max_code_width)
                        formatted_lines.append(
                            Back.BLACK
                            + Fore.WHITE
                            + " │"
                            + Back.WHITE
                            + Fore.BLACK
                            + " "
                            + padded
                            + " "
                            + Back.BLACK
                            + Fore.WHITE
                            + "│"
                        )
                formatted_lines.append(
                    Back.BLACK + Fore.WHITE + " └" + "─" * max_code_width + "┘"
                )
                formatted_lines.append("")
                code_block_lines = []
                in_code_block = False
            else:
                # Start of code block
                code_block_lang = line.strip()[3:].strip()
                in_code_block = True
                if code_block_lang:
                    formatted_lines.append("")
                    formatted_lines.append(Fore.BLACK + Style.DIM + "   Code: " + code_block_lang)
            continue

        if in_code_block:
            code_block_lines.append(line)
            continue

        # Format headers (# Header)
        if line.strip().startswith("#"):
            header_match = re.match(r"^(#+)\s*(.+)", line.strip())
            if header_match:
                level = len(header_match.group(1))
                header_text = header_match.group(2).strip()
                formatted_lines.append("")
                if level == 1:
                    formatted_lines.append(
                        Fore.CYAN + Style.BRIGHT + Style.UNDERLINE + "  " + header_text
                    )
                elif level == 2:
                    formatted_lines.append(Fore.CYAN + Style.BRIGHT + "  " + header_text)
                else:
                    formatted_lines.append(Fore.CYAN + "  " + header_text)
                formatted_lines.append("")
            continue

        # Format lists (- or * or numbered)
        list_match = re.match(r"^(\s*)([-*•]|\d+\.)\s+(.+)", line)
        if list_match:
            indent = len(list_match.group(1))
            list_content = list_match.group(3).strip()
            formatted_lines.append(
                " " * indent + Fore.YELLOW + "• " + Fore.WHITE + list_content
            )
            continue

        # Regular paragraph text - apply all formatting
        if line.strip():
            formatted_line = line

            # Format bold (**text**)
            formatted_line = re.sub(
                r"\*\*([^*]+)\*\*", lambda m: Style.BRIGHT + m.group(1) + Style.RESET_ALL, formatted_line
            )

            # Format inline code (`code`)
            formatted_line = re.sub(
                r"`([^`]+)`",
                lambda m: Back.BLACK
                + Fore.WHITE
                + " "
                + m.group(1)
                + " "
                + Style.RESET_ALL,
                formatted_line,
            )

            # Word wrap for long lines (80 chars)
            max_width = 78
            # Remove ANSI codes for length calculation
            plain_text = re.sub(r"\x1b\[[0-9;]*m", "", formatted_line)
            if len(plain_text) > max_width:
                # Simple word wrap
                words = formatted_line.split()
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    # Check length without ANSI codes
                    test_plain = re.sub(r"\x1b\[[0-9;]*m", "", test_line)
                    if len(test_plain) > max_width and current_line.strip():
                        formatted_lines.append(Fore.WHITE + "  " + current_line.strip())
                        current_line = word + " "
                    else:
                        current_line = test_line
                if current_line.strip():
                    formatted_lines.append(Fore.WHITE + "  " + current_line.strip())
            else:
                formatted_lines.append(Fore.WHITE + "  " + formatted_line)
        else:
            # Empty line for spacing
            formatted_lines.append("")

    # Handle code block if still open at end
    if in_code_block and code_block_lines:
        formatted_lines.append("")
        max_code_width = 76
        formatted_lines.append(
            Back.BLACK + Fore.WHITE + " ┌" + "─" * max_code_width + "┐"
        )
        for code_line in code_block_lines:
            if len(code_line) > max_code_width:
                for j in range(0, len(code_line), max_code_width):
                    chunk = code_line[j : j + max_code_width]
                    padded = chunk.ljust(max_code_width)
                    formatted_lines.append(
                        Back.BLACK
                        + Fore.WHITE
                        + " │"
                        + Back.WHITE
                        + Fore.BLACK
                        + " "
                        + padded
                        + " "
                        + Back.BLACK
                        + Fore.WHITE
                        + "│"
                    )
            else:
                padded = code_line.ljust(max_code_width)
                formatted_lines.append(
                    Back.BLACK
                    + Fore.WHITE
                    + " │"
                    + Back.WHITE
                    + Fore.BLACK
                    + " "
                    + padded
                    + " "
                    + Back.BLACK
                    + Fore.WHITE
                    + "│"
                )
        formatted_lines.append(
            Back.BLACK + Fore.WHITE + " └" + "─" * max_code_width + "┘"
        )
        formatted_lines.append("")

    return "\n".join(formatted_lines)


def show_help():
    """Display help message."""
    print(Fore.CYAN + Style.BRIGHT + "\n🤖 Talk CLI - Gemini AI Command Line Interface\n")
    print(Fore.YELLOW + "Usage:")
    print(Fore.WHITE + "  piptalk [--model <model>] [prompt]")
    print(Fore.WHITE + "  piptalk -m <model> [prompt]")
    print(Fore.WHITE + "  piptalk --help | -h\n")

    print(Fore.YELLOW + "Options:")
    print(
        Fore.CYAN + "  --model, -m <model>" + Fore.WHITE + "  Select a specific Gemini model"
    )
    print(Fore.CYAN + "  --help, -h" + Fore.WHITE + "          Show this help message\n")

    print(Fore.YELLOW + "Available models:")
    for key in MODEL_MAP:
        print(
            Fore.CYAN
            + f"  {key:<12} : {MODEL_MAP[key]['display']}"
        )

    print(Fore.YELLOW + "\nExamples:")
    print(Fore.WHITE + '  piptalk --model flash "Hello world"')
    print(Fore.WHITE + '  piptalk -m 2.0-flash "Quick question"')
    print(Fore.WHITE + '  piptalk -m 2.5-pro "Explain quantum computing"')
    print(Fore.WHITE + '  piptalk "What is machine learning?"')
    print(Fore.WHITE + "  piptalk                          # Interactive mode\n")

    print(
        Fore.BLACK
        + Style.DIM
        + "For more information, visit: https://www.npmjs.com/package/@karitkeyaranjan/talk-cli\n"
    )


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Talk CLI - Gemini AI Command Line Interface",
        add_help=False,
    )
    parser.add_argument(
        "-m",
        "--model",
        default="flash",
        help="Select a Gemini model",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="Show help message",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Your prompt/question",
    )

    args, unknown = parser.parse_known_args()

    # Handle help
    if args.help or "-h" in sys.argv or "--help" in sys.argv:
        show_help()
        sys.exit(0)

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or API_KEY
    if not api_key:
        print(Fore.RED + "❌ Please set GEMINI_API_KEY environment variable.")
        sys.exit(1)

    # Validate model
    selected_model = args.model.lower()
    if selected_model not in MODEL_MAP:
        print(Fore.RED + f"❌ Invalid model: {selected_model}")
        print(Fore.YELLOW + "\nAvailable models:")
        for key in MODEL_MAP:
            print(Fore.CYAN + f"  - {key}: {MODEL_MAP[key]['display']}")
        sys.exit(1)

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL_MAP[selected_model]["name"])
    model_display = MODEL_MAP[selected_model]["display"]

    # Get prompt
    prompt = " ".join(args.prompt) if args.prompt else None

    # Show selected model if no prompt provided
    if not prompt:
        print(Fore.BLACK + Style.DIM + f"Using model: {model_display}\n")

    # Get prompt if not provided
    if not prompt:
        try:
            prompt = input(Fore.CYAN + "🤖 Enter your prompt: ")
        except (EOFError, KeyboardInterrupt):
            print("\n")
            sys.exit(0)

    if not prompt:
        print(Fore.RED + "❌ No prompt provided.")
        sys.exit(1)

    try:
        print(Fore.WHITE + "\n⏳ Generating response...\n")

        response = model.generate_content(prompt)
        output = response.text

        # Display the header with styling
        print(Fore.BLUE + Style.BRIGHT + "\n" + "╔" + "═" * 78 + "╗")
        print(Fore.BLUE + Style.BRIGHT + "║" + " " * 78 + "║")
        title = f"{model_display} Response"
        title_padding = (78 - len(title)) // 2
        print(
            Fore.BLUE
            + Style.BRIGHT
            + "║"
            + " " * title_padding
            + title
            + " " * (78 - len(title) - title_padding)
            + "║"
        )
        print(Fore.BLUE + Style.BRIGHT + "║" + " " * 78 + "║")
        print(Fore.BLUE + Style.BRIGHT + "╚" + "═" * 78 + "╝")
        print("")

        # Display the formatted response
        formatted_output = format_response(output)
        print(formatted_output)

        # Display footer
        print(Fore.WHITE + "\n" + "─" * 80 + "\n")

    except Exception as e:
        print(Fore.RED + Style.BRIGHT + "❌ Error: " + Fore.RED + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

