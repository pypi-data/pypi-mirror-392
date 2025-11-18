# Destination: tests/test_renderer.py

"""
Tests for LayerRenderer abstraction.
"""

import pytest
import time
from PIL import Image

from catpic.framebuffer import FrameBuffer
from catpic.renderer import LayerRenderer
from catpic.protocols.core import encode_png


@pytest.fixture
def framebuffer():
    """Create a test framebuffer."""
    return FrameBuffer('glyxel', 80, 24)


@pytest.fixture
def renderer(framebuffer):
    """Create a renderer with test framebuffer."""
    return LayerRenderer(framebuffer)


@pytest.fixture
def test_layers():
    """Create test layers with timing."""
    img = Image.new('RGB', (16, 16), (255, 0, 0))
    png_data = encode_png(img)
    
    return [
        {'data': png_data, 'render_at_ms': 0},
        {'data': png_data, 'render_at_ms': 50},
        {'data': png_data, 'render_at_ms': 100},
    ]


class TestLayerRendererCreation:
    """Test renderer creation."""
    
    def test_create_with_framebuffer(self, framebuffer):
        """Can create renderer with framebuffer."""
        renderer = LayerRenderer(framebuffer)
        assert renderer.fb is framebuffer


class TestLayerRendering:
    """Test basic layer rendering."""
    
    def test_render_single_layer(self, renderer, test_layers, capsys):
        """Can render single layer."""
        renderer.render_layer(test_layers[0]['data'])
        # Should produce output
        captured = capsys.readouterr()
        assert len(captured.out) > 0 or len(captured.err) > 0
    
    def test_render_with_clear(self, renderer, test_layers, capsys):
        """Can render layer with clearing."""
        renderer.render_layer(test_layers[0]['data'], clear_previous=True)
        # Should not raise


class TestSequenceRendering:
    """Test sequence rendering with timing."""
    
    def test_render_sequence(self, renderer, test_layers):
        """Can render sequence of layers."""
        start = time.time()
        renderer.render_sequence(test_layers)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # Should take at least 100ms (last frame timing)
        # Allow some slack for execution time
        assert elapsed >= 90  # 100ms - 10ms slack
    
    def test_render_empty_sequence(self, renderer):
        """Rendering empty sequence does not raise."""
        renderer.render_sequence([])
    
    def test_render_single_frame_sequence(self, renderer, test_layers):
        """Can render single frame."""
        renderer.render_sequence([test_layers[0]])


class TestLoopRendering:
    """Test loop rendering."""
    
    def test_render_once(self, renderer, test_layers):
        """Loop count 1 renders once."""
        start = time.time()
        renderer.render_with_loop(test_layers, loop_count=1)
        elapsed = (time.time() - start) * 1000
        
        # Should take ~100ms for single iteration
        assert 90 <= elapsed <= 200
    
    def test_render_twice(self, renderer, test_layers):
        """Loop count 2 renders twice."""
        # Use shorter delays for faster test
        short_layers = [
            {'data': test_layers[0]['data'], 'render_at_ms': 0},
            {'data': test_layers[1]['data'], 'render_at_ms': 20},
        ]
        
        start = time.time()
        renderer.render_with_loop(short_layers, loop_count=2)
        elapsed = (time.time() - start) * 1000
        
        # Should take ~40ms (20ms * 2 iterations)
        assert 35 <= elapsed <= 120
    
    def test_render_empty_with_loop(self, renderer):
        """Rendering empty sequence with loop does not raise."""
        renderer.render_with_loop([], loop_count=5)


class TestTiming:
    """Test timing accuracy."""
    
    def test_timing_accuracy(self, renderer):
        """Renderer respects frame timing."""
        # Create layers with specific delays
        img = Image.new('RGB', (16, 16), (255, 0, 0))
        png_data = encode_png(img)
        
        layers = [
            {'data': png_data, 'render_at_ms': 0},
            {'data': png_data, 'render_at_ms': 50},
        ]
        
        start = time.time()
        renderer.render_sequence(layers)
        elapsed = (time.time() - start) * 1000
        
        # Should take at least 50ms
        assert elapsed >= 45  # Allow 5ms slack
    
    def test_no_delay_for_immediate_frames(self, renderer, test_layers):
        """Immediate frames (render_at_ms=0) don't delay."""
        immediate_layers = [
            {'data': test_layers[0]['data'], 'render_at_ms': 0},
            {'data': test_layers[1]['data'], 'render_at_ms': 0},
        ]
        
        start = time.time()
        renderer.render_sequence(immediate_layers)
        elapsed = (time.time() - start) * 1000
        
        # Should be very fast (< 50ms for two immediate frames)
        assert elapsed < 50
