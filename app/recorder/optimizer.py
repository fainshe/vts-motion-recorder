import numpy as np
from scipy.signal import savgol_filter


class MotionOptimizer:
    def __init__(self, smoothing_window: int = 3, threshold: float = 0.001):
        self.smoothing_window = max(3, smoothing_window | 1)
        self.threshold = threshold

    def smooth(self, frames: list[dict]) -> list[dict]:
        if len(frames) < self.smoothing_window:
            return frames

        param_names = list(frames[0]["params"].keys())
        if not param_names:
            return frames

        times = [f["time"] for f in frames]
        param_arrays = {}

        for name in param_names:
            values = [f["params"].get(name, 0.0) for f in frames]
            arr = np.array(values)
            try:
                window = min(self.smoothing_window, len(arr) // 2 * 2 - 1)
                if window >= 3:
                    smoothed = savgol_filter(arr, window, polyorder=2)
                    param_arrays[name] = smoothed.tolist()
                else:
                    param_arrays[name] = values
            except Exception:
                param_arrays[name] = values

        return [
            {
                "time": times[i],
                "params": {name: param_arrays[name][i] for name in param_names}
            }
            for i in range(len(frames))
        ]

    def remove_duplicates(self, frames: list[dict]) -> list[dict]:
        if len(frames) <= 1:
            return frames

        result = [frames[0]]
        for i in range(1, len(frames)):
            prev = frames[i - 1]["params"]
            curr = frames[i]["params"]
            is_duplicate = all(
                abs(curr.get(k, 0) - prev.get(k, 0)) < self.threshold
                for k in set(list(prev.keys()) + list(curr.keys()))
            )
            if not is_duplicate:
                result.append(frames[i])

        return result

    def reduce_keyframes(self, frames: list[dict], tolerance: float = 0.5) -> list[dict]:
        if len(frames) <= 2:
            return frames

        def douglas_peucker(points, tol):
            if len(points) <= 2:
                return points

            max_dist = 0
            max_idx = 0
            first = points[0]
            last = points[-1]

            for i in range(1, len(points) - 1):
                dist = self._perpendicular_dist(points[i], first, last)
                if dist > max_dist:
                    max_dist = dist
                    max_idx = i

            if max_dist > tol:
                left = douglas_peucker(points[:max_idx + 1], tol)
                right = douglas_peucker(points[max_idx:], tol)
                return left[:-1] + right
            else:
                return [first, last]

        param_names = list(frames[0]["params"].keys())
        reduced_indices = set()

        for name in param_names:
            points = [(f["time"], f["params"].get(name, 0.0)) for f in frames]
            reduced = douglas_peucker(points, tolerance)
            reduced_times = {p[0] for p in reduced}
            reduced_indices.update(
                i for i, f in enumerate(frames) if f["time"] in reduced_times
            )

        return [frames[i] for i in sorted(reduced_indices)]

    @staticmethod
    def _perpendicular_dist(point, line_start, line_end):
        line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
        line_len_sq = line_vec[0]**2 + line_vec[1]**2
        if line_len_sq == 0:
            return ((point[0] - line_start[0])**2 + (point[1] - line_start[1])**2) ** 0.5
        t = max(0, min(1, ((point[0] - line_start[0]) * line_vec[0] +
                           (point[1] - line_start[1]) * line_vec[1]) / line_len_sq))
        projection = (line_start[0] + t * line_vec[0], line_start[1] + t * line_vec[1])
        return ((point[0] - projection[0])**2 + (point[1] - projection[1])**2) ** 0.5

    def optimize(self, frames: list[dict], smooth: bool = True, remove_dupes: bool = True, reduce_kf: bool = False) -> list[dict]:
        result = frames.copy()
        if smooth:
            result = self.smooth(result)
        if remove_dupes:
            result = self.remove_duplicates(result)
        if reduce_kf:
            result = self.reduce_keyframes(result)
        return result
