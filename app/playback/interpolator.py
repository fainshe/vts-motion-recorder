class Interpolator:
    @staticmethod
    def interpolate(frames: list[dict], target_time: float) -> dict[str, float]:
        if not frames:
            return {}

        if target_time <= frames[0]["time"]:
            return frames[0]["params"].copy()

        if target_time >= frames[-1]["time"]:
            return frames[-1]["params"].copy()

        lower = frames[0]
        upper = frames[-1]

        for i in range(len(frames) - 1):
            if frames[i]["time"] <= target_time <= frames[i + 1]["time"]:
                lower = frames[i]
                upper = frames[i + 1]
                break

        t_lower = lower["time"]
        t_upper = upper["time"]
        t_diff = t_upper - t_lower

        if t_diff == 0:
            return lower["params"].copy()

        t = (target_time - t_lower) / t_diff
        result = {}

        all_keys = set(list(lower["params"].keys()) + list(upper["params"].keys()))
        for key in all_keys:
            v_lower = lower["params"].get(key, 0.0)
            v_upper = upper["params"].get(key, 0.0)
            result[key] = v_lower + (v_upper - v_lower) * t

        return result
