from canal_delights.core.engine import DrawingEngine


class RecordingPathEngine:
    draw_path = DrawingEngine.draw_path

    def __init__(self):
        self.strokes = []
        self.fills = []

    def draw_polyline(self, points, color, width, close=False):
        self.strokes.append((points, color, width, close))

    def _fill_polygon(self, points, color):
        self.fills.append((points, color))


def test_open_path_does_not_close_its_stroke_or_fill():
    engine = RecordingPathEngine()
    engine.draw_path([['M', 0, 0], ['L', 10, 0], ['L', 10, 10]], (1, 2, 3), (4, 5, 6))

    assert engine.fills == []
    assert engine.strokes[0][0] == [(0, 0), (10, 0), (10, 10)]
    assert engine.strokes[0][-1] is False


def test_closed_path_can_fill():
    engine = RecordingPathEngine()
    engine.draw_path([['M', 0, 0], ['L', 10, 0], ['L', 10, 10], ['Z']], (1, 2, 3))

    assert engine.fills[0][0][-1] == (0, 0)
