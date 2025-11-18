from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="Project")


@_attrs_define
class Project:
    """
    Attributes:
        organization (str):
        name (str):
        framework (str):
        simulator (str):
    """

    organization: str
    name: str
    framework: str
    simulator: str

    def to_dict(self) -> dict[str, Any]:
        organization = self.organization

        name = self.name

        framework = self.framework

        simulator = self.simulator

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization": organization,
                "name": name,
                "framework": framework,
                "simulator": simulator,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization = d.pop("organization")

        name = d.pop("name")

        framework = d.pop("framework")

        simulator = d.pop("simulator")

        project = cls(
            organization=organization,
            name=name,
            framework=framework,
            simulator=simulator,
        )

        return project
