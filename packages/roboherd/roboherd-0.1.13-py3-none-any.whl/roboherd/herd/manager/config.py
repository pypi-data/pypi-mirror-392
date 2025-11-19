from pydantic import BaseModel, Field

from dataclasses import dataclass, field

from roboherd.cow import RoboCow
from .load import load_cow


class ConfigOverrides(BaseModel):
    """Values used in `roboherd.toml` to overide the default
    values in the imported cow. This class is meant as a
    reference, and not meant to be directly used."""

    name: str | None = Field(
        default=None, description="set to override the name", examples=["New name"]
    )
    handle: str | None = Field(
        default=None, description="set to override the handle", examples=["new-handle"]
    )
    base_url: str | None = Field(
        default=None,
        description="set to override the base url",
        examples=["https://other.example"],
    )
    skip_profile_update: bool | None = Field(
        default=None, description="set to skip updating the profile", examples=[True]
    )


@dataclass
class CowConfig:
    name: str = field(metadata={"description": "Name of the cow, must be unique"})
    module: str
    attribute: str
    config: dict

    @staticmethod
    def from_name_and_dict(name, cow: dict) -> "CowConfig":
        module, attribute = cow["bot"].split(":")

        return CowConfig(name=name, module=module, attribute=attribute, config=cow)

    def load(self) -> RoboCow:
        cow = load_cow(self.module, self.attribute)

        overrides = ConfigOverrides(**self.config)

        for value in ["name", "handle", "base_url"]:
            if getattr(overrides, value):
                setattr(cow.information, value, getattr(overrides, value))

        if overrides.skip_profile_update:
            cow.skip_profile_update = overrides.skip_profile_update

        return cow

    def __hash__(self):
        return hash(self.name)


@dataclass
class HerdConfig:
    cows: list[CowConfig] = field(default_factory=list)

    def for_name(self, name: str) -> CowConfig | None:
        for cow in self.cows:
            if cow.name == name:
                return cow
        return None

    @property
    def names(self) -> set[str]:
        return {cow.name for cow in self.cows}

    @staticmethod
    def from_settings(settings):
        cows = [
            CowConfig.from_name_and_dict(name, config)
            for name, config in settings.cow.items()
        ]

        return HerdConfig(cows=cows)

    def load_herd(self) -> list[RoboCow]:
        return [cow.load() for cow in self.cows]
