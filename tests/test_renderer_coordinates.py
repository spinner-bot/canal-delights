from canal_delights.core.renderer import DrawingDataParser


class RecordingEngine:
    def draw_rect(self, *args):
        self.rect = args


def test_rect_uses_canvas_width_and_height_independently():
    engine = RecordingEngine()
    parser = DrawingDataParser(engine)

    parser._render_rect([.1, .2, .8, .5], {'fill': (1, 2, 3)}, (0, 0, 1200, 800), None)

    assert engine.rect[:4] == (120.0, 160.0, 960.0, 400.0)
