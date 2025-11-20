from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, distribution, version
from typing import Literal

from bear_shelf._internal._version import __commit_id__, __version__, __version_tuple__


@dataclass(slots=True)
class _Package:
    """Dataclass to store package information."""

    name: str
    """Package name."""
    version: str = "0.0.0"
    """Package version."""
    description: str = "No description available."
    """Package description."""

    def __str__(self) -> str:
        """String representation of the package information."""
        return f"{self.name} v{self.version}: {self.description}"


def _get_package_info(dist: str) -> _Package:
    """Get package information for the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        Package information with version, name, and description.
    """
    return _Package(name=dist, version=_get_version(dist), description=_get_description(dist))


def _get_version(dist: str) -> str:
    """Get version of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    try:
        return version(dist)
    except PackageNotFoundError:
        return "0.0.0"


def _get_description(dist: str) -> str:
    """Get description of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A description string.
    """
    try:
        return distribution(dist).metadata.get("summary", "No description available.")
    except PackageNotFoundError:
        return "No description available."


@dataclass(slots=True, frozen=True)
class _ProjectName:
    """A class to represent the project name and its metadata as literals for type safety.

    This is done this way to make it easier to see the values in the IDE and to ensure that the values are consistent throughout the codebase.
    """

    package_distribution: Literal["bear-shelf"] = "bear-shelf"
    project: Literal["bear_shelf"] = "bear_shelf"
    project_upper: Literal["BEAR_SHELF"] = "BEAR_SHELF"
    env_variable: Literal["BEAR_SHELF_ENV"] = "BEAR_SHELF_ENV"


def project_version() -> str:
    """Get the current project version.

    Returns:
        The current project version string.
    """
    return __version__ if __version__ != "0.0.0" else _get_version("bear-shelf")


@dataclass(slots=True)
class _ProjectMetadata:
    """Dataclass to store the current project metadata."""

    _name: _ProjectName = field(default_factory=_ProjectName)
    version: str = field(default_factory=project_version)
    version_tuple: tuple[int, int, int] = field(default=__version_tuple__)
    commit_id: str = field(default=__commit_id__)

    def __str__(self) -> str:
        """String representation of the project metadata."""
        return f"{self.full_version}: {self.description}"

    @property
    def full_version(self) -> str:
        """Get the full version string."""
        return f"{self.name} v{self.version}"

    @property
    def description(self) -> str:
        """Get the project description from the distribution metadata."""
        return _get_description(self.name)

    @property
    def name(self) -> Literal["bear-shelf"]:
        """Get the package distribution name."""
        return self._name.package_distribution

    @property
    def name_upper(self) -> Literal["BEAR_SHELF"]:
        """Get the project name in uppercase with underscores."""
        return self._name.project_upper

    @property
    def project_name(self) -> Literal["bear_shelf"]:
        """Get the project name."""
        return self._name.project

    @property
    def env_variable(self) -> Literal["BEAR_SHELF_ENV"]:
        """Get the environment variable name for the project.

        Used to check if the project is running in a specific environment.
        """
        return self._name.env_variable


METADATA = _ProjectMetadata()


__all__ = ["METADATA"]
