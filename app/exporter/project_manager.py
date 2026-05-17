from pathlib import Path
from .json_exporter import MotionExporter


class ProjectManager:
    def __init__(self, motions_dir: str = "data/motions", projects_dir: str = "data/projects"):
        self.motions_dir = Path(motions_dir)
        self.projects_dir = Path(projects_dir)
        self.motions_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def save_motion(self, motion_data: dict, filename: str, compressed: bool = False) -> Path:
        if compressed:
            filepath = self.motions_dir / f"{filename}.motion.gz"
            return MotionExporter.save_compressed(motion_data, filepath)
        else:
            filepath = self.motions_dir / f"{filename}.json"
            return MotionExporter.save_json(motion_data, filepath)

    def load_motion(self, filepath: str | Path) -> dict:
        path = Path(filepath)
        if path.suffix == ".gz":
            return MotionExporter.load_compressed(path)
        return MotionExporter.load_json(path)

    def save_project(self, motion_data: dict, project_name: str) -> Path:
        filepath = self.projects_dir / f"{project_name}.motionproj"
        return MotionExporter.save_project(motion_data, filepath)

    def load_project(self, filepath: str | Path) -> dict:
        return MotionExporter.load_project(filepath)

    def list_motions(self) -> list[Path]:
        files = []
        for ext in ["*.json", "*.motion.gz"]:
            files.extend(self.motions_dir.glob(ext))
        return sorted(files)

    def list_projects(self) -> list[Path]:
        return sorted(self.projects_dir.glob("*.motionproj"))
