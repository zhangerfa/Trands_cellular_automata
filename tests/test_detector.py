from tca.detector.detector import Detector
from tca.models.vehicle import Vehicle


class TestDetector:
    def test_detect_within_range(self):
        det = Detector(start_time=0, end_time=100, start_x=10, end_x=50)
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 5
        det.detect(time=10, vehicles=[v])
        assert v.id in det._active

    def test_detect_outside_time_range(self):
        det = Detector(start_time=50, end_time=100, start_x=0, end_x=100)
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 5
        det.detect(time=10, vehicles=[v])
        assert v.id not in det._active

    def test_detect_outside_space_range(self):
        det = Detector(start_time=0, end_time=100, start_x=30, end_x=50)
        v = Vehicle(id=1, lane=0, x=20)
        det.detect(time=10, vehicles=[v])
        assert v.id not in det._active

    def test_vehicle_enter_then_exit(self):
        det = Detector(start_time=0, end_time=100, start_x=10, end_x=50)
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 3
        det.detect(time=0, vehicles=[v])
        assert v.id in det._active
        v.x = 60
        det.detect(time=1, vehicles=[v])
        assert v.id not in det._active
        assert len(det._completed) == 1

    def test_flow_increments_on_exit(self):
        det = Detector(start_time=0, end_time=100, start_x=10, end_x=50)
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 3
        det.detect(time=0, vehicles=[v])
        v.x = 60
        det.detect(time=1, vehicles=[v])
        assert det.flow == 1

    def test_speed_recording(self):
        det = Detector(start_time=0, end_time=100, start_x=0, end_x=100)
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 4
        det.detect(time=0, vehicles=[v])
        v.v = 6
        det.detect(time=1, vehicles=[v])
        record = det._active[v.id]
        assert record["v_sum"] == 10
        assert record["detect_times"] == 2

    def test_summary(self):
        det = Detector(start_time=0, end_time=100, start_x=0, end_x=100)
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 4
        det.detect(time=0, vehicles=[v])
        v.v = 6
        det.detect(time=1, vehicles=[v])
        v.x = 200
        det.detect(time=2, vehicles=[v])
        summary = det.summary()
        assert summary["average_speed"] == 5.0
        assert summary["flow"] == 1

    def test_to_dataframe(self):
        det = Detector(start_time=0, end_time=100, start_x=0, end_x=100)
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 4
        det.detect(time=0, vehicles=[v])
        v.x = 200
        det.detect(time=1, vehicles=[v])
        df = det.to_dataframe()
        assert len(df) == 1

    def test_default_detects_all(self):
        det = Detector()
        v = Vehicle(id=1, lane=0, x=20)
        v.v = 3
        det.detect(time=0, vehicles=[v])
        assert v.id in det._active
