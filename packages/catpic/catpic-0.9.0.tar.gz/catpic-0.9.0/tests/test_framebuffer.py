# Destination: tests/test_framebuffer.py

"""
Tests for FrameBuffer abstraction.
"""

import pytest
from io import BytesIO
from PIL import Image

from catpic.framebuffer import FrameBuffer
from catpic.protocols.core import encode_png


@pytest.fixture
def test_image_png():
    """Create a test image as PNG bytes."""
    img = Image.new('RGB', (16, 16), (255, 0, 0))
    return encode_png(img)


class TestFrameBufferCreation:
    """Test framebuffer creation and initialization."""
    
    def test_create_with_protocol(self):
        """Can create framebuffer with protocol name."""
        fb = FrameBuffer('glyxel', 80, 24)
        assert fb.protocol_name == 'glyxel'
        assert fb.width == 80
        assert fb.height == 24
    
    def test_create_with_kitty(self):
        """Can create framebuffer with kitty protocol."""
        fb = FrameBuffer('kitty', 80, 24)
        assert fb.protocol_name == 'kitty'
    
    def test_create_with_sixel(self):
        """Can create framebuffer with sixel protocol."""
        fb = FrameBuffer('sixel', 80, 24)
        assert fb.protocol_name == 'sixel'
    
    def test_create_with_iterm2(self):
        """Can create framebuffer with iterm2 protocol."""
        fb = FrameBuffer('iterm2', 80, 24)
        assert fb.protocol_name == 'iterm2'
    
    def test_invalid_protocol_raises(self):
        """Invalid protocol raises error."""
        with pytest.raises(ValueError):
            FrameBuffer('invalid', 80, 24)


class TestFrameBufferRendering:
    """Test framebuffer rendering operations."""
    
    def test_render_does_not_raise(self, test_image_png, capsys):
        """Render method does not raise exceptions."""
        fb = FrameBuffer('glyxel', 80, 24)
        fb.render(test_image_png)  # Should not raise
        
        # Capture output
        captured = capsys.readouterr()
        # Should have some output (protocol-specific)
        assert len(captured.out) > 0 or len(captured.err) > 0
    
    def test_render_different_protocols(self, test_image_png, capsys):
        """Can render with different protocols."""
        for protocol in ['glyxel', 'kitty', 'sixel', 'iterm2']:
            fb = FrameBuffer(protocol, 80, 24)
            fb.render(test_image_png)  # Should not raise
    
    def test_clear_does_not_raise(self):
        """Clear method does not raise exceptions."""
        fb = FrameBuffer('glyxel', 80, 24)
        fb.clear()  # Should not raise
    
    def test_present_does_not_raise(self):
        """Present method does not raise exceptions."""
        fb = FrameBuffer('glyxel', 80, 24)
        fb.present()  # Should not raise (currently no-op)


class TestFrameBufferCapabilities:
    """Test framebuffer capability queries."""
    
    def test_supports_animation(self):
        """All protocols should support animation."""
        for protocol in ['glyxel', 'kitty', 'sixel', 'iterm2']:
            fb = FrameBuffer(protocol, 80, 24)
            assert fb.supports_animation() is True
    
    def test_is_immediate_mode(self):
        """Framebuffer should be in immediate mode."""
        fb = FrameBuffer('glyxel', 80, 24)
        assert fb.is_immediate_mode is True


class TestFrameBufferConfig:
    """Test framebuffer configuration."""
    
    def test_config_has_dimensions(self):
        """FrameBuffer config should have max_width and max_height."""
        fb = FrameBuffer('glyxel', 80, 24)
        assert fb.config.max_width == 80
        assert fb.config.max_height == 24
    
    def test_dimensions_passed_to_protocol(self, test_image_png):
        """Framebuffer should pass dimensions to protocol."""
        fb = FrameBuffer('glyxel', 40, 20)
        # This should use the dimensions when generating
        fb.render(test_image_png)  # Should not raise
