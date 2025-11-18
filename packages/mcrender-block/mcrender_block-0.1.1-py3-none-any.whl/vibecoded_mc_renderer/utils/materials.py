"""Material color registry for GregTech and other mods."""

from typing import Dict, Tuple, Optional


# GregTech material colors (RGB tuples 0-255)
# Based on common GregTech material appearances
GREGTECH_MATERIALS: Dict[str, Tuple[int, int, int]] = {
    # Common Metals
    "copper": (255, 100, 0),
    "tin": (220, 220, 220),
    "bronze": (255, 128, 0),
    "brass": (255, 180, 0),
    "steel": (128, 128, 128),
    "iron": (200, 200, 200),
    "gold": (255, 255, 0),
    "silver": (220, 220, 255),
    "lead": (140, 100, 140),
    "nickel": (200, 200, 150),
    "zinc": (250, 250, 210),
    "aluminum": (128, 200, 240),
    "aluminium": (128, 200, 240),
    
    # Advanced Alloys
    "invar": (180, 184, 150),
    "electrum": (255, 255, 100),
    "cupronickel": (227, 179, 160),
    "kanthal": (194, 157, 145),
    "nichrome": (205, 206, 246),
    "red_alloy": (200, 0, 0),
    "blue_alloy": (100, 120, 200),
    
    # Stainless Steels
    "stainless_steel": (200, 200, 220),
    "damascus_steel": (110, 109, 113),
    "black_steel": (100, 100, 120),
    "blue_steel": (100, 120, 180),
    "red_steel": (180, 100, 100),
    
    # High-tier Materials
    "titanium": (220, 160, 240),
    "tungsten": (50, 50, 50),
    "tungstensteel": (100, 100, 160),
    "chrome": (255, 230, 230),
    "iridium": (240, 240, 245),
    "osmium": (50, 50, 255),
    "platinum": (255, 255, 200),
    "palladium": (128, 128, 128),
    
    # Super Materials
    "naquadah": (50, 50, 50),
    "naquadah_alloy": (40, 40, 50),
    "neutronium": (250, 250, 250),
    "duranium": (80, 90, 110),
    "tritanium": (120, 100, 140),
    
    # Silicon & Semiconductors
    "silicon": (60, 60, 80),
    "gallium_arsenide": (160, 160, 140),
    
    # Plastics & Polymers
    "rubber": (30, 30, 30),
    "polyethylene": (200, 200, 200),
    "polytetrafluoroethylene": (100, 100, 100),
    "epoxy": (200, 140, 20),
    "silicone_rubber": (220, 220, 220),
    "polybenzimidazole": (44, 44, 44),
    
    # Gems & Crystals
    "diamond": (200, 255, 255),
    "emerald": (80, 255, 80),
    "ruby": (255, 100, 100),
    "sapphire": (100, 100, 255),
    "olivine": (150, 255, 150),
    "topaz": (255, 128, 0),
    "tanzanite": (64, 0, 200),
    "amethyst": (210, 50, 210),
    "opal": (0, 0, 255),
    "jasper": (200, 80, 80),
    
    # Rare Earth
    "neodymium": (100, 100, 100),
    "samarium": (255, 255, 200),
    "yttrium": (220, 250, 220),
    
    # Radioactive
    "uranium": (50, 240, 50),
    "plutonium": (240, 50, 50),
    "thorium": (0, 30, 0),
    
    # Common Materials
    "coal": (70, 70, 70),
    "charcoal": (90, 70, 70),
    "sulfur": (255, 255, 0),
    "saltpeter": (230, 230, 230),
    "redstone": (200, 0, 0),
    "glowstone": (255, 255, 0),
    "glass": (250, 250, 250),
    
    # Wood Types
    "wood": (150, 100, 50),
    "rubber_wood": (180, 150, 100),
    "treated_wood": (100, 80, 40),
}


# Voltage tier colors (for machine casings)
VOLTAGE_TIER_COLORS: Dict[str, Tuple[int, int, int]] = {
    "ulv": (180, 180, 180),
    "lv": (254, 254, 254),
    "mv": (255, 168, 86),
    "hv": (255, 251, 1),
    "ev": (127, 127, 127),
    "iv": (72, 233, 244),
    "luv": (254, 127, 156),
    "zpm": (255, 0, 255),
    "uv": (0, 255, 0),
    "uhv": (0, 170, 255),
    "uev": (0, 0, 139),
    "uiv": (139, 0, 0),
    "uxv": (0, 100, 0),
    "opv": (128, 0, 128),
    "max": (255, 255, 255),
}


class MaterialColorRegistry:
    """Registry for material colors with fallback support."""
    
    def __init__(self):
        """Initialize the registry with default GregTech materials."""
        self.materials = GREGTECH_MATERIALS.copy()
        self.voltage_tiers = VOLTAGE_TIER_COLORS.copy()
    
    def get_material_color(self, material_name: str) -> Optional[Tuple[int, int, int]]:
        """
        Get the RGB color for a material.
        
        Args:
            material_name: Material identifier (lowercase with underscores)
        
        Returns:
            RGB tuple (0-255) or None if not found
        """
        # Normalize material name
        material_name = material_name.lower().strip()
        return self.materials.get(material_name)
    
    def get_tier_color(self, tier: str) -> Optional[Tuple[int, int, int]]:
        """
        Get the RGB color for a voltage tier.
        
        Args:
            tier: Voltage tier identifier (ulv, lv, mv, etc.)
        
        Returns:
            RGB tuple (0-255) or None if not found
        """
        tier = tier.lower().strip()
        return self.voltage_tiers.get(tier)
    
    def register_material(self, name: str, color: Tuple[int, int, int]) -> None:
        """
        Register a custom material color.
        
        Args:
            name: Material name
            color: RGB tuple (0-255)
        """
        self.materials[name.lower()] = color
    
    def register_tier(self, tier: str, color: Tuple[int, int, int]) -> None:
        """
        Register a custom voltage tier color.
        
        Args:
            tier: Tier identifier
            color: RGB tuple (0-255)
        """
        self.voltage_tiers[tier.lower()] = color
    
    def list_materials(self) -> list[str]:
        """Get list of all registered material names."""
        return sorted(self.materials.keys())
    
    def list_tiers(self) -> list[str]:
        """Get list of all registered voltage tiers."""
        return sorted(self.voltage_tiers.keys())


# Global registry instance
_global_registry = MaterialColorRegistry()


def get_material_color(material: str) -> Optional[Tuple[int, int, int]]:
    """Get material color from global registry."""
    return _global_registry.get_material_color(material)


def get_tier_color(tier: str) -> Optional[Tuple[int, int, int]]:
    """Get voltage tier color from global registry."""
    return _global_registry.get_tier_color(tier)


def register_material(name: str, color: Tuple[int, int, int]) -> None:
    """Register material in global registry."""
    _global_registry.register_material(name, color)


def register_tier(tier: str, color: Tuple[int, int, int]) -> None:
    """Register tier in global registry."""
    _global_registry.register_tier(tier, color)


def list_materials() -> list[str]:
    """List all materials in global registry."""
    return _global_registry.list_materials()


def list_tiers() -> list[str]:
    """List all tiers in global registry."""
    return _global_registry.list_tiers()
