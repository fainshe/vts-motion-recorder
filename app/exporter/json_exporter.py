import json
import gzip
from pathlib import Path
from datetime import datetime, timezone


class MotionExporter:
    @staticmethod
    def save_json(motion_data: dict, filepath: str | Path) -> Path:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(motion_data, indent=2))
        return path

    @staticmethod
    def save_compressed(motion_data: dict, filepath: str | Path) -> Path:
        path = Path(filepath)
        if not path.suffix:
            path = path.with_suffix(".motion.gz")
        path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(motion_data).encode("utf-8")
        path.write_bytes(gzip.compress(data, compresslevel=9))
        return path

    @staticmethod
    def load_json(filepath: str | Path) -> dict:
        path = Path(filepath)
        return json.loads(path.read_text())

    @staticmethod
    def load_compressed(filepath: str | Path) -> dict:
        path = Path(filepath)
        data = gzip.decompress(path.read_bytes())
        return json.loads(data)

    @staticmethod
    def save_project(motion_data: dict, filepath: str | Path) -> Path:
        path = Path(filepath)
        if not path.suffix:
            path = path.with_suffix(".motionproj")
        path.parent.mkdir(parents=True, exist_ok=True)

        project = {
            "version": "1.0",
            "type": "motion_project",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "motion": motion_data,
        }
        path.write_text(json.dumps(project, indent=2))
        return path

    @staticmethod
    def load_project(filepath: str | Path) -> dict:
        path = Path(filepath)
        project = json.loads(path.read_text())
        return project.get("motion", {})
