from tca.models.enums import Direction, Color


class TestDirection:
    def test_right_value(self):
        assert Direction.RIGHT.value == 1

    def test_left_value(self):
        assert Direction.LEFT.value == -1

    def test_opposite(self):
        assert Direction.RIGHT.opposite() == Direction.LEFT
        assert Direction.LEFT.opposite() == Direction.RIGHT

    def test_iteration_order(self):
        dirs = list(Direction)
        assert len(dirs) == 2


class TestColor:
    def test_color_values_are_rgb_tuples(self):
        assert Color.RED.value == (1, 0, 0)
        assert Color.BLUE.value == (0, 0, 1)
        assert Color.GREEN.value == (0, 1, 0)
        assert Color.BLACK.value == (0, 0, 0)
