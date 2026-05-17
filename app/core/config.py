from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    vts_host: str = "127.0.0.1"
    vts_port: int = 8002
    plugin_name: str = "Live2D Motion Recorder"
    plugin_developer: str = "Fainshe"
    config_file: str = "vts_config.json"

    default_fps: int = 60
    max_recording_seconds: int = 3600
    buffer_chunk_size: int = 1000

    smoothing_enabled: bool = True
    smoothing_window: int = 3
    duplicate_threshold: float = 0.001

    data_dir: Path = field(default_factory=lambda: Path("data"))
    motions_dir: Path = field(default_factory=lambda: Path("data/motions"))
    projects_dir: Path = field(default_factory=lambda: Path("data/projects"))

    def __post_init__(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.motions_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)


config = AppConfig()
