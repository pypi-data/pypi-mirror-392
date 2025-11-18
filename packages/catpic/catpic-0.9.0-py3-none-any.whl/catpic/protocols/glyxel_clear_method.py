# Destination: src/catpic/protocols/glyxel.py
# MODIFICATION: Add this method to the GlyxelGenerator class

# Add after the can_optimize() method:

    def clear(self) -> bytes:
        """
        Clear glyxel output using ANSI escape sequences.
        
        Returns cursor to home position and clears the screen.
        This is used for animation to clear the previous frame.
        
        Returns:
            ANSI escape sequence to clear and reset cursor
        """
        # ESC[H moves cursor to home (1,1)
        # ESC[2J clears entire screen
        return b'\x1b[H\x1b[2J'
