from dataclasses import dataclass, field


@dataclass
class ParameterInfo:
    name: str
    value: float = 0.0
    min_value: float = -30.0
    max_value: float = 30.0
    default_value: float = 0.0


@dataclass
class LiveParameters:
    timestamp: float = 0.0
    parameters: dict[str, float] = field(default_factory=dict)

    def get(self, name: str, default: float = 0.0) -> float:
        return self.parameters.get(name, default)


@dataclass
class PluginAuth:
    plugin_name: str
    plugin_developer: str
    plugin_token: str = ""
