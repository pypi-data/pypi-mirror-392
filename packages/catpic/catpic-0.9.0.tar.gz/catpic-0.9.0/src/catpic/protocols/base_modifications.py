# Destination: src/catpic/protocols/base.py
# MODIFICATION: Add these two methods to the ProtocolGenerator class

# Add after the can_optimize() method:

    def clear(self) -> bytes:
        """
        Generate escape sequence to clear previous output.
        
        Used for animation to clear the previous frame before displaying
        the next one. Default implementation returns empty bytes (no clearing).
        
        Protocols should override this if they need specific clearing logic:
        - Glyxel: ANSI cursor positioning and clear sequences
        - Kitty/Sixel/iTerm2: May not need explicit clearing (image replacement)
        
        Returns:
            Escape sequence to clear display, or empty bytes
        """
        return b''
    
    def supports_animation(self) -> bool:
        """
        Check if protocol supports efficient frame sequences.
        
        Returns True for protocols that can handle animation efficiently
        (kitty, sixel, iterm2 can replace images in place).
        Returns False for protocols where animation is expensive.
        
        Default: True (most protocols support animation reasonably well)
        
        Returns:
            True if protocol supports efficient animation
        """
        return True
