"""A set of general-purpose Pydantic models and utilities."""

import json
from typing import Any, ClassVar, Literal, Self, overload
from xml.etree.ElementTree import Element, tostring

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SecretStr,
    SerializerFunctionWrapHandler,
    field_serializer,
    field_validator,
    model_serializer,
)
from pydantic.fields import FieldInfo

from codec_cub.xmls.helpers import to_elem


class FrozenModel(BaseModel):
    """A Pydantic model that is immutable after creation."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ExtraIgnoreModel(BaseModel):
    """A Pydantic model that ignores extra fields."""

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)


class LowRentPydanticMixin:
    """A mixin that provides Pydantic-like dump methods for non-Pydantic classes."""

    def model_dump(
        self,
        *,
        exclude_none: bool = False,
        exclude: set[str] | tuple[str] | list[str] | None = None,
    ) -> dict[str, Any]:
        """Return a dictionary representation of the model.

        Args:
            exclude_none: If True, exclude None values from the output.

        Returns:
            A dictionary containing the model's attributes.
        """
        data: dict[str, Any] = {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}

        if exclude is not None:
            for key in exclude:
                data.pop(key, None)

        return data

    def model_dump_json(self, *, exclude_none: bool = False, indent: int | None = None) -> str:
        """Return a JSON string representation of the model.

        Args:
            exclude_none: If True, exclude None values from the output.
            indent: Number of spaces for indentation (None for compact output).

        Returns:
            A JSON string representation of the model.
        """
        return json.dumps(self.model_dump(exclude_none=exclude_none), indent=indent)


def extract_field_attrs[T](
    model: type[BaseModel],
    expected_type: type[T],
    attr: str = "default",
) -> dict[str, T]:
    """Extract specified attribute from model fields if of expected type.

    Args:
        model: Pydantic model class
        expected_type: Expected type of the attribute value
        attr: Attribute name to extract (default: "default")

    Returns:
        Dictionary of field names to attribute values
    """
    extracted: dict[str, T] = {}
    for field_name, field in model.model_fields.items():
        if isinstance(field, FieldInfo) and hasattr(field, "annotation"):
            attr_value: Any | None = getattr(field, attr, None)
            if isinstance(attr_value, expected_type):
                extracted[field_name] = attr_value
    return extracted


class AbstractElement:
    """Abstract base class for XML elements with a tag attribute."""

    tag: ClassVar[str]

    def to_xml(self) -> Element:
        """Convert the model attributes to an XML element.

        Returns:
            An XML Element representing the model.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class BaseElement[T: AbstractElement](BaseModel, AbstractElement):
    """Base model for XML elements with a tag attribute."""

    model_config = {"arbitrary_types_allowed": True}

    tag: ClassVar[str] = ""
    sub_elements: list[T] = Field(default_factory=list, description="Sub-elements of other XML elements.")

    @model_serializer(mode="wrap")
    def convert_to_strings(self, nxt: SerializerFunctionWrapHandler) -> dict[Any, Any]:
        """Convert common types to strings for XML serialization."""
        data: dict[Any, Any] = nxt(self)

        for key, value in data.items():
            if value is None:
                continue
            if isinstance(value, (int | float | bool)):
                data[key] = str(value).lower()
        return data

    def add(self, element: T) -> Self:
        """Add a sub-element to the list of sub-elements."""
        if not isinstance(element, BaseElement):
            raise TypeError(f"Expected an instance of BaseElement, got {type(element)}")
        self.sub_elements.append(element)
        return self

    def has_element(self, element: type[T] | str) -> bool:
        """Check if the element is present in the sub-elements."""
        if isinstance(element, str):
            return any(sub.tag == element for sub in self.sub_elements)
        if isinstance(element, type) and issubclass(element, BaseElement):
            return any(isinstance(sub, element) for sub in self.sub_elements)
        return element in self.sub_elements

    def has_field(self, attr: type | str) -> bool:
        """Check if the class has a specific field or attribute."""
        if isinstance(attr, str):
            return hasattr(self, attr)
        return hasattr(self, attr.__name__)

    @overload
    def get(self, element: str, strict: Literal[True]) -> T: ...

    @overload
    def get(self, element: type[T], strict: Literal[True]) -> T: ...

    @overload
    def get(self, element: type[T], strict: Literal[False] = False) -> T | None: ...

    @overload
    def get(self, element: str, strict: Literal[False] = False) -> T | None: ...

    def get(self, element: type[T] | str, strict: bool = False) -> T | None:
        """Get the sub-element by element type or tag name.

        Args:
            element: The type or tag name of the sub-element to retrieve.
            strict: If True, raise an error if the element is not found. Defaults to False

        Returns:
            The sub-element if found, otherwise None or raises an error if strict is True.
        """
        if isinstance(element, type):
            for sub in self.sub_elements:
                if isinstance(sub, element):
                    return sub
        elif isinstance(element, str):
            for sub in self.sub_elements:
                if sub.tag == element:
                    return sub
        if strict:
            raise ValueError(f"Element '{element}' not found in sub_elements")
        return None

    def get_req(self, element: T | str) -> T:
        """Get the sub-element by element type or tag name, raising an error if not found."""
        return self.get(element, strict=True)

    def to_xml(self, exclude_none: bool = True, exclude: set | None = None, **kwargs) -> Element:
        """Convert the model attributes to an XML element.

        Returns:
            An XML Element representing the model.
        """
        if exclude is None:
            exclude_me: set[str] = {"sub_elements"}
        else:
            exclude_me: set[str] = exclude.union({"sub_elements"})
        element: Element = to_elem(
            tag=self.tag,
            **self.model_dump(
                exclude_none=exclude_none,
                exclude=exclude_me,
                **kwargs,
            ),
        )
        if self.sub_elements:
            for sub_element in self.sub_elements:
                sub_element_element: Element = sub_element.to_xml()
                element.append(sub_element_element)
        return element

    def to_string(self) -> str:
        """Convert the model to a string representation."""
        return tostring(self.to_xml(), encoding="unicode")


class SecretModel(RootModel[SecretStr | None]):
    """A model to securely handle secrets that can be reused."""

    model_config = ConfigDict(frozen=True, validate_by_name=True)
    root: SecretStr | None = Field(default=None, alias="secret")

    @field_validator("root", mode="before")
    @classmethod
    def convert_secret(cls, v: Any) -> SecretStr | None:
        """Convert a string to SecretStr."""
        if isinstance(v, str):
            if v.lower() in {"null", "none", "****", ""}:
                return None
            return SecretStr(v)
        return v

    @field_serializer("root", mode="wrap")
    def serialize_path(self, value: Any, nxt: SerializerFunctionWrapHandler) -> str:
        """Serialize the secret to a string."""
        secret_value: SecretStr | None = nxt(value)
        if secret_value is None:
            return "null"
        return "****"

    def get_secret_value(self) -> str:
        """Get the secret value as a string."""
        if self.root is None:
            raise ValueError("Secret is not set")
        return self.root.get_secret_value()

    def is_null(self) -> bool:
        """Check if the secret is None."""
        return self.root is None

    def __str__(self) -> str:
        return str(self.root)

    def __repr__(self) -> str:
        return repr(self.root)

    @classmethod
    def load(cls, secret: str | SecretStr | None = None) -> Self:
        """Create a Secret from a string."""
        return cls.model_construct(root=cls.convert_secret(secret))


class TokenModel(SecretModel):
    """A model to securely handle tokens."""

    root: SecretStr | None = Field(default=None, alias="token")


class Password(SecretModel):
    """A model to securely handle passwords."""

    root: SecretStr | None = Field(default=None, alias="password")
