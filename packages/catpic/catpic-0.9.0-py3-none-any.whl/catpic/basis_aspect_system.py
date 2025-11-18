# Destination: src/catpic/core.py (UPDATE - add to existing file)

"""
Basis-aware aspect ratio correction system.

Each basis has different pixel arrangements that interact with terminal
font metrics differently. This matrix provides relative corrections.

The base aspect ratio (2.0) assumes a typical terminal where characters
are roughly 2x taller than wide. The corrections adjust for how different
basis configurations compress/stretch visuals.
"""

# Internal basis correction matrix
# Format: {(basis_x, basis_y): correction_multiplier}
# These are relative adjustments to the base aspect ratio (2.0)
# Values determined through visual tuning in typical terminal
BASIS_ASPECT_CORRECTIONS = {
    (1, 2): 2.0,    # 1x2: 2 vertical pixels - needs 2x correction (4.0 effective)
    (2, 2): 0.9,    # 2x2: 4 pixels in 2x2 grid - slight correction (1.8 effective)
    (2, 3): 1.5,    # 2x3: 6 pixels - moderate correction (3.0 effective)
    (2, 4): 2.0,    # 2x4: 8 pixels - strong correction (4.0 effective)
}

# Base aspect ratio for typical terminals (chars are ~2x taller than wide)
BASE_CHAR_ASPECT = 2.0


def get_char_aspect(basis: Optional[BASIS] = None) -> float:
    """
    Get character aspect ratio with basis-specific correction.
    
    Uses CATPIC_CONFIG for aspect ratios.
    
    Args:
        basis: BASIS enum value (if None, returns base aspect only)
    
    Returns:
        Corrected character aspect ratio for this basis
    """
    # Try to load from config
    try:
        from .config import load_config
        config = load_config()
        
        if basis is None:
            return config.get('aspect base', BASE_CHAR_ASPECT)
        
        # Get basis-specific aspect
        basis_x, basis_y = basis.value
        basis_key = f"aspect {basis_x}x{basis_y}"
        
        if basis_key in config:
            return config[basis_key]
        
        # Fall back to base aspect with internal correction
        base_aspect = config.get('aspect base', BASE_CHAR_ASPECT)
        correction = BASIS_ASPECT_CORRECTIONS.get((basis_x, basis_y), 1.0)
        return base_aspect * correction
        
    except Exception:
        # Config system not available, use legacy approach
        base_aspect = float(os.getenv('CATPIC_CHAR_ASPECT', BASE_CHAR_ASPECT))
        
        if basis is None:
            return base_aspect
        
        basis_x, basis_y = basis.value
        correction = BASIS_ASPECT_CORRECTIONS.get((basis_x, basis_y), 1.0)
        return base_aspect * correction


# Update existing get_char_aspect() function with this new implementation
# Remove the old simple version that just reads CATPIC_CHAR_ASPECT