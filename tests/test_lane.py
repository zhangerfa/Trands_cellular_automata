from tca.models.lane import Lane


class TestLane:
    def test_length_single_section(self):
        lane = Lane({"普通车道": 100})
        assert lane.length == 100

    def test_length_multiple_sections(self):
        lane = Lane({"普通车道": 100, "施工路段": 50})
        assert lane.length == 150

    def test_section_at_single(self):
        lane = Lane({"普通车道": 100})
        assert lane.section_at(0) == "普通车道"
        assert lane.section_at(50) == "普通车道"
        assert lane.section_at(99) == "普通车道"

    def test_section_at_multiple(self):
        lane = Lane({"普通车道": 100, "施工路段": 50})
        assert lane.section_at(0) == "普通车道"
        assert lane.section_at(99) == "普通车道"
        assert lane.section_at(100) == "施工路段"
        assert lane.section_at(149) == "施工路段"

    def test_section_at_out_of_range(self):
        lane = Lane({"普通车道": 100})
        assert lane.section_at(100) is None
        assert lane.section_at(200) is None
