from canal_delights.core.renderer import DrawingDataParser


class RecordingEngine:
    def draw_rect(self, *args):
        self.rect = args


def test_rect_uses_canvas_width_and_height_independently():
    engine = RecordingEngine()
    parser = DrawingDataParser(engine)

    parser._render_rect([.1, .2, .8, .5], {'fill': (1, 2, 3)}, (0, 0, 1200, 800), None)

    assert engine.rect[:4] == (120.0, 160.0, 960.0, 400.0)


class CircleRecordingEngine:
    def draw_circle(self, *args):
        self.circle = args


def test_group_transform_is_applied_once():
    engine = CircleRecordingEngine()
    parser = DrawingDataParser(engine)
    parser.parse([
        ['GR', [['C', [.5, .5, .1], {'fill': (1, 2, 3)}]], {
            'transform': {'scale': [.5, .5], 'translate': [.1, 0], 'pivot': [.5, .5]},
        }],
    ], (0, 0, 100, 100))

    assert engine.circle[:3] == (60.0, 50.0, 5.0)


class PointRecordingEngine:
    def draw_point(self, *args):
        self.point = args


def test_point_size_is_in_pixels_and_inherits_scale():
    engine = PointRecordingEngine()
    parser = DrawingDataParser(engine)
    parser.parse([
        ['GR', [['P', [.5, .5, 3], {'fill': (1, 2, 3)}]], {
            'transform': {'scale': [.5, .5], 'pivot': [.5, .5]},
        }],
    ], (0, 0, 1200, 800))

    assert engine.point[:3] == (600.0, 400.0, 1.5)
