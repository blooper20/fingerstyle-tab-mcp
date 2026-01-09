"""
Configuration management for Fingerstyle Tab MCP Server
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    supported_formats: List[str] = field(default_factory=lambda: ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'])
    default_bpm: float = 120.0
    min_bpm: int = 40
    max_bpm: int = 200


@dataclass
class TablatureConfig:
    """Tablature generation configuration"""
    standard_tuning: List[str] = field(default_factory=lambda: ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'])
    bass_threshold: int = 50
    slots_per_measure: int = 16
    measures_per_line: int = 4
    min_fret: int = 0
    max_fret: int = 15
    preferred_fret_max: int = 5


@dataclass
class ChordDetectionConfig:
    """Chord detection configuration"""
    min_score: int = 5
    enabled_chord_types: Dict[str, bool] = field(default_factory=lambda: {
        'major': True,
        'minor': True,
        'seventh': True,
        'major_seventh': True,
        'minor_seventh': True,
        'suspended': True,
        'add9': True,
    })


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None


@dataclass
class I18nConfig:
    """Internationalization configuration"""
    default_language: str = "en"
    fallback: bool = True


@dataclass
class MCPConfig:
    """MCP server configuration"""
    server_name: str = "Fingerstyle Tab Generator"
    detailed_errors: bool = True


@dataclass
class Config:
    """Main configuration class"""
    audio: AudioConfig = field(default_factory=AudioConfig)
    tablature: TablatureConfig = field(default_factory=TablatureConfig)
    chord_detection: ChordDetectionConfig = field(default_factory=ChordDetectionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    i18n: I18nConfig = field(default_factory=I18nConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)

    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """
        Load configuration from a YAML file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            Config object with loaded settings

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data is None:
                logger.warning(f"Empty configuration file: {config_path}, using defaults")
                return cls()

            return cls(
                audio=AudioConfig(**data.get('audio', {})),
                tablature=TablatureConfig(**data.get('tablature', {})),
                chord_detection=ChordDetectionConfig(**data.get('chord_detection', {})),
                logging=LoggingConfig(**data.get('logging', {})),
                i18n=I18nConfig(**data.get('i18n', {})),
                mcp=MCPConfig(**data.get('mcp', {})),
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {str(e)}") from e
        except TypeError as e:
            raise ValueError(f"Invalid configuration format: {str(e)}") from e

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """
        Load configuration from file or use defaults.

        Args:
            config_path: Optional path to config file. If not provided,
                        searches for config.yaml in current directory and
                        parent directories.

        Returns:
            Config object
        """
        if config_path:
            return cls.from_yaml(config_path)

        # Search for config.yaml in current and parent directories
        search_paths = [
            Path.cwd() / "config.yaml",
            Path(__file__).parent.parent / "config.yaml",
        ]

        for path in search_paths:
            if path.exists():
                logger.info(f"Loading configuration from: {path}")
                return cls.from_yaml(str(path))

        logger.info("No configuration file found, using defaults")
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'audio': self.audio.__dict__,
            'tablature': self.tablature.__dict__,
            'chord_detection': self.chord_detection.__dict__,
            'logging': self.logging.__dict__,
            'i18n': self.i18n.__dict__,
            'mcp': self.mcp.__dict__,
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config.load(config_path)
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """
    Reload the global configuration.

    Args:
        config_path: Optional path to configuration file

    Returns:
        New Config instance
    """
    global _config
    _config = Config.load(config_path)
    return _config
