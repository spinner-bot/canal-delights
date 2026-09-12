class FakePen:
    def __init__(self):
        self.clear_count = 0

    def clear(self):
        self.clear_count += 1

    def up(self):
        pass


def test_pure_engine_can_clear_one_layer_without_touching_others():
    from canal_delights.core.engine import DrawingEngine

    engine = DrawingEngine.__new__(DrawingEngine)
    background = FakePen()
    content = FakePen()
    engine._pens = {'background': background, 'content': content}

    engine.clear('content')

    assert background.clear_count == 0
    assert content.clear_count == 1
