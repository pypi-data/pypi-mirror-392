# Destination: src/catpic/cli.py (UPDATE - modify protocol handling section)

"""
Add this import at the top:
"""
from .detection import detect_best_protocol, supports_protocol

"""
Update the display command's protocol handling:
"""

@app.command()
def display(
    filepath: str = typer.Argument(..., help="Path to .meow file"),
    protocol: Optional[str] = typer.Option(
        None, 
        "--protocol", 
        "-p",
        help="Display protocol (auto/glyxel/kitty/sixel/iterm2). Default: auto-detect"
    ),
    meld: bool = typer.Option(False, "--meld", help="Force runtime melding"),
):
    """
    Display a MEOW file in the terminal.
    
    By default, automatically detects the best available protocol.
    Use --protocol to force a specific protocol.
    """
    # Auto-detect protocol if not specified
    if protocol is None or protocol == 'auto':
        protocol = detect_best_protocol()
        if protocol != 'glyxel':
            # Inform user of auto-detected protocol (but not for glyxel fallback)
            typer.echo(f"Auto-detected: {protocol}", err=True)
    else:
        # Validate protocol is supported
        if not supports_protocol(protocol):
            typer.echo(f"Warning: Protocol '{protocol}' may not be supported by this terminal", err=True)
    
    content = load_meow_file(filepath)
    display_meow(content, meld=meld, protocol=protocol)


@app.command()
def encode(
    image_path: str = typer.Argument(..., help="Path to image file"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output .meow file"),
    width: Optional[int] = typer.Option(None, "-w", "--width", help="Width in characters"),
    height: Optional[int] = typer.Option(None, "-h", "--height", help="Height in characters"),
    basis: Optional[str] = typer.Option(None, "--basis", help="Basis level (1,2 | 2,2 | 2,3 | 2,4)"),
    protocol: Optional[str] = typer.Option(
        None,
        "--protocol",
        "-p", 
        help="Protocol mode (glyxel | glyxel_only). Default: glyxel (dual content)"
    ),
):
    """
    Encode an image to MEOW format.
    
    Default protocol is 'glyxel' which creates dual-content files:
    - PNG in cells field (for protocol display)
    - Glyxel ANSI (for cat compatibility)
    
    Use --protocol=glyxel_only for minimal file size (glyxel only).
    """
    # Parse basis if provided
    basis_enum = None
    if basis:
        try:
            parts = basis.split(',')
            if len(parts) != 2:
                raise ValueError("Basis must be in format 'x,y'")
            bx, by = int(parts[0]), int(parts[1])
            basis_enum = BASIS((bx, by))
        except (ValueError, KeyError) as e:
            typer.echo(f"Error: Invalid basis '{basis}': {e}", err=True)
            raise typer.Exit(1)
    
    # Create encoder
    encoder = CatpicEncoder(basis=basis_enum)
    
    # Check if animated
    try:
        with Image.open(image_path) as img:
            is_animated = getattr(img, "is_animated", False)
    except Exception as e:
        typer.echo(f"Error: Cannot open image: {e}", err=True)
        raise typer.Exit(EXIT_ERROR_FILE_NOT_FOUND)
    
    # Encode
    try:
        if is_animated:
            output_str = encoder.encode_animation(
                image_path,
                width=width,
                height=height,
                protocol=protocol,
            )
        else:
            output_str = encoder.encode_image(
                image_path,
                width=width,
                height=height,
                protocol=protocol,
            )
    except Exception as e:
        typer.echo(f"Error: Encoding failed: {e}", err=True)
        raise typer.Exit(EXIT_ERROR_GENERAL)
    
    # Output
    if output:
        save_meow_file(output, output_str)
        content_type = "glyxel only" if protocol == "glyxel_only" else "dual content: PNG + glyxel"
        typer.echo(f"Saved to {output} ({content_type})")
    else:
        print(output_str, end='')


@app.command()
def detect():
    """
    Detect terminal capabilities and show supported protocols.
    
    This is useful for debugging protocol detection and understanding
    what graphics protocols your terminal supports.
    """
    from .detection import get_detector
    
    detector = get_detector()
    capabilities = detector.detect_capabilities(use_cache=False)
    
    typer.echo("Terminal Capability Detection")
    typer.echo("=" * 40)
    typer.echo()
    
    # Show environment info
    typer.echo("Environment:")
    env_vars = ['TERM', 'KITTY_WINDOW_ID', 'TERM_PROGRAM', 'LC_TERMINAL']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            typer.echo(f"  {var}={value}")
    typer.echo()
    
    # Show detected capabilities
    typer.echo("Detected Protocols:")
    for cap in capabilities:
        if cap.value == 'glyxel':
            typer.echo(f"  ✓ {cap.value} (universal fallback)")
        else:
            typer.echo(f"  ✓ {cap.value}")
    
    typer.echo()
    typer.echo(f"Best Protocol: {detector.select_best_protocol()}")
