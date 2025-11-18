"""
Typing Tool Module - Built-in Telugu Typing Functionality
Auto-transliteration on spacebar press
"""

import tkinter as tk
from tkinter import scrolledtext, Menu
from .transliterator import roman_to_telugu


class TeluguTyper:
    """Simple Telugu Typing Tool with auto-transliteration"""

    def __init__(self, title="Telugu Typing Tool", font_size=20):
        """
        Initialize Telugu Typing Tool

        Args:
            title (str): Window title
            font_size (int): Font size for text area
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("700x500")

        self.font_size = font_size
        self.current_word = ""

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        # Top instruction bar
        instruction = tk.Label(
            self.root,
            text="Type in Roman letters and press SPACE to convert to Telugu!",
            font=('Arial', 11, 'bold'),
            bg='#4A90E2',
            fg='white',
            pady=8
        )
        instruction.pack(fill=tk.X)

        # Text area
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            font=('Noto Sans Telugu', self.font_size),
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status bar
        self.status = tk.Label(
            self.root,
            text="Ready - Type something...",
            font=('Arial', 9),
            bg='lightgray',
            anchor='w',
            padx=5
        )
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

        # Bind events
        self.text_area.bind('<KeyPress>', self._on_key_press)
        self.text_area.bind('<space>', self._on_space_press)
        self.text_area.bind('<Return>', self._on_enter_press)

        # Add example text
        example = "Examples - Type these and press SPACE:\n"
        example += "namaste, krishna, rama, amma, pusthakam\n\n"
        example += "Start typing below:\n" + "="*50 + "\n\n"
        self.text_area.insert('1.0', example)
        self.text_area.mark_set(tk.INSERT, tk.END)
        self.text_area.focus()

    def _on_key_press(self, event):
        """Handle regular key press"""
        if event.char and event.char.isalnum():
            self.current_word += event.char
            self.status.config(text=f"Typing: {self.current_word}")

    def _on_space_press(self, event):
        """Handle spacebar - convert to Telugu"""
        if self.current_word:
            # Get cursor position
            cursor_pos = self.text_area.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            start_pos = f"{line}.{int(col) - len(self.current_word)}"

            # Transliterate
            telugu_text = roman_to_telugu(self.current_word)

            # Replace Roman with Telugu
            self.text_area.delete(start_pos, cursor_pos)
            self.text_area.insert(start_pos, telugu_text)

            # Update status
            self.status.config(text=f"✓ {self.current_word} → {telugu_text}")

            # Clear buffer
            self.current_word = ""

        return None

    def _on_enter_press(self, event):
        """Handle enter key"""
        self.current_word = ""
        return None

    def run(self):
        """Start the typing tool"""
        self.root.mainloop()


def start_typing_tool(title="Telugu Typing Tool", font_size=20):
    """
    Start the Telugu typing tool

    Args:
        title (str): Window title
        font_size (int): Font size for text

    Example:
        >>> from my_telugu_lib import start_typing_tool
        >>> start_typing_tool()
    """
    typer = TeluguTyper(title=title, font_size=font_size)
    typer.run()


def convert_on_space(text):
    """
    Convert a text string with space-separated Roman words to Telugu

    Args:
        text (str): Space-separated Roman words

    Returns:
        str: Telugu text

    Example:
        >>> from my_telugu_lib import convert_on_space
        >>> convert_on_space("namaste rama")
        'నమస్తే రమ'
    """
    words = text.split()
    telugu_words = [roman_to_telugu(word) for word in words]
    return ' '.join(telugu_words)


def interactive_typing():
    """
    Interactive command-line typing tool
    Type Roman text, press Enter to see Telugu conversion

    Example:
        >>> from my_telugu_lib import interactive_typing
        >>> interactive_typing()
    """
    print("="*60)
    print("Telugu Interactive Typing Tool")
    print("="*60)
    print("\nType Roman text and press ENTER to convert to Telugu")
    print("Type 'quit' or 'exit' to stop\n")

    while True:
        try:
            user_input = input("Type (Roman): ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if user_input:
                telugu = convert_on_space(user_input)
                print(f"Telugu: {telugu}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


# Convenience alias
typing_tool = start_typing_tool
