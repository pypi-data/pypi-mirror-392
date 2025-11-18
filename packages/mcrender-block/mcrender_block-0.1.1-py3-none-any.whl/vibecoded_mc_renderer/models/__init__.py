"""Data models for Minecraft blocks."""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


@dataclass
class Face:
    """Represents a face of a model element."""

    texture: str
    uv: Optional[List[float]] = None
    cullface: Optional[str] = None
    rotation: int = 0
    tintindex: int = -1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Face":
        """Create a Face from a dictionary."""
        return cls(
            texture=data.get("texture", "#missing"),
            uv=data.get("uv"),
            cullface=data.get("cullface"),
            rotation=data.get("rotation", 0),
            tintindex=data.get("tintindex", -1),
        )


@dataclass
class ModelElement:
    """Represents a cuboid element in a block model."""

    from_pos: List[float]
    to_pos: List[float]
    faces: Dict[str, Face]
    rotation: Optional[Dict[str, Any]] = None
    shade: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelElement":
        """Create a ModelElement from a dictionary."""
        faces = {
            face_name: Face.from_dict(face_data)
            for face_name, face_data in data.get("faces", {}).items()
        }
        return cls(
            from_pos=data.get("from", [0, 0, 0]),
            to_pos=data.get("to", [16, 16, 16]),
            faces=faces,
            rotation=data.get("rotation"),
            shade=data.get("shade", True),
        )


@dataclass
class BlockModel:
    """Represents a Minecraft block model."""

    parent: Optional[str] = None
    textures: Dict[str, str] = field(default_factory=dict)
    elements: List[ModelElement] = field(default_factory=list)
    ambientocclusion: bool = True
    display: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockModel":
        """Create a BlockModel from a dictionary."""
        elements = [ModelElement.from_dict(elem) for elem in data.get("elements", [])]
        return cls(
            parent=data.get("parent"),
            textures=data.get("textures", {}),
            elements=elements,
            ambientocclusion=data.get("ambientocclusion", True),
            display=data.get("display", {}),
        )

    def resolve_textures(self, parent_model: Optional["BlockModel"] = None) -> Dict[str, str]:
        """
        Resolve all texture variables by merging with parent textures.
        Returns a complete texture map with all variables resolved.
        """
        resolved = {}

        # Start with parent textures if available
        if parent_model:
            resolved.update(parent_model.textures)

        # Override with own textures
        resolved.update(self.textures)

        # Resolve texture variables (e.g., "#all" -> "block/stone")
        max_iterations = 10  # Prevent infinite loops
        for _ in range(max_iterations):
            changed = False
            for key, value in list(resolved.items()):
                if isinstance(value, str) and value.startswith("#"):
                    # Reference to another texture variable
                    ref_key = value[1:]  # Remove '#'
                    if ref_key in resolved and not resolved[ref_key].startswith("#"):
                        resolved[key] = resolved[ref_key]
                        changed = True
            if not changed:
                break

        return resolved


@dataclass
class ModelVariant:
    """Represents a model variant in a blockstate."""

    model: str
    x: int = 0
    y: int = 0
    uvlock: bool = False
    weight: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelVariant":
        """Create a ModelVariant from a dictionary."""
        if isinstance(data, str):
            # Simple case: just a model path
            return cls(model=data)
        return cls(
            model=data.get("model", ""),
            x=data.get("x", 0),
            y=data.get("y", 0),
            uvlock=data.get("uvlock", False),
            weight=data.get("weight", 1),
        )


@dataclass
class Blockstate:
    """Represents a Minecraft blockstate definition."""

    variants: Dict[str, List[ModelVariant]] = field(default_factory=dict)
    multipart: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Blockstate":
        """Create a Blockstate from a dictionary."""
        blockstate = cls()

        # Handle variants format
        if "variants" in data:
            for state, variant_data in data["variants"].items():
                if isinstance(variant_data, list):
                    blockstate.variants[state] = [
                        ModelVariant.from_dict(v) for v in variant_data
                    ]
                else:
                    blockstate.variants[state] = [ModelVariant.from_dict(variant_data)]

        # Handle multipart format
        if "multipart" in data:
            blockstate.multipart = data["multipart"]

        return blockstate

    def get_default_model(self) -> Optional[str]:
        """Get the default model path for this blockstate."""
        # For variants, try to find the simplest state or use first available
        if self.variants:
            # Try common default states
            for default_state in ["", "normal", "facing=north", "axis=y"]:
                if default_state in self.variants:
                    return self.variants[default_state][0].model

            # Fall back to first variant
            first_key = next(iter(self.variants))
            return self.variants[first_key][0].model

        # For multipart, return first model (this is simplified)
        if self.multipart:
            for part in self.multipart:
                if "apply" in part:
                    apply_data = part["apply"]
                    if isinstance(apply_data, dict) and "model" in apply_data:
                        return apply_data["model"]
                    elif isinstance(apply_data, list) and apply_data:
                        return apply_data[0].get("model")

        return None
