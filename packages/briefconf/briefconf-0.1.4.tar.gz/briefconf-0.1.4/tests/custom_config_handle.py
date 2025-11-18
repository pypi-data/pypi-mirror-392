import logging.config
from dataclasses import dataclass
from typing import ClassVar, Self

from briefconf.v0 import BriefConfig


@dataclass(frozen=True, slots=True)
class CustomConfig(BriefConfig):
    _key4merge_files: ClassVar[str] = "include"

    data_dir: str

    @classmethod
    def load(cls, config_path: str) -> Self:
        configs = cls._load_config(config_path)
        logging.config.dictConfig(configs["logging"])

        return cls(
            data_dir=configs['data_dir'],
        )
