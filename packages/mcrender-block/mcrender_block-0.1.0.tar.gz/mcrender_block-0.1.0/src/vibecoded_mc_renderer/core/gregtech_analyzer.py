"""Analyzer for GregTech mod resources and structure."""

from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import re

from vibecoded_mc_renderer.core.resource_manager import ResourceManager


class GregTechAnalyzer:
    """Analyzes GregTech mod structure to discover materials, tiers, and machines."""
    
    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize GregTech analyzer.
        
        Args:
            resource_manager: ResourceManager with GregTech jar/extracted files
        """
        self.resource_manager = resource_manager
        self._materials_cache: Optional[Set[str]] = None
        self._material_sets_cache: Optional[Set[str]] = None
        self._machines_cache: Optional[Dict[str, Dict[str, bool]]] = None
        self._voltage_tiers_cache: Optional[Set[str]] = None
    
    def discover_materials(self) -> Set[str]:
        """
        Discover available materials by scanning material_sets textures.
        
        Returns:
            Set of material names (copper, steel, aluminum, etc.)
        """
        if self._materials_cache is not None:
            return self._materials_cache
        
        materials = set()
        
        # Scan for material_sets/{material}/ patterns
        # Look for textures like assets/gregtech/textures/blocks/material_sets/dull/copper.png
        texture_path_pattern = re.compile(
            r"assets/gregtech/textures/blocks/material_sets/[^/]+/([^/]+)\.png"
        )
        
        for resource_path in self.resource_manager.resource_index.keys():
            match = texture_path_pattern.match(resource_path)
            if match:
                material_name = match.group(1)
                materials.add(material_name)
        
        self._materials_cache = materials
        return materials
    
    def discover_material_sets(self) -> Set[str]:
        """
        Discover available material set styles (dull, shiny, metallic, etc.).
        
        Returns:
            Set of material set names
        """
        if self._material_sets_cache is not None:
            return self._material_sets_cache
        
        material_sets = set()
        
        # Scan for material_sets/{set_name}/ patterns
        texture_path_pattern = re.compile(
            r"assets/gregtech/textures/blocks/material_sets/([^/]+)/"
        )
        
        for resource_path in self.resource_manager.resource_index.keys():
            match = texture_path_pattern.match(resource_path)
            if match:
                set_name = match.group(1)
                material_sets.add(set_name)
        
        self._material_sets_cache = material_sets
        return material_sets
    
    def discover_machines(self) -> Dict[str, Dict[str, bool]]:
        """
        Discover available machines with their overlay capabilities.
        
        Returns:
            Dict mapping machine name to dict of capabilities:
            {
                "electric_furnace": {
                    "has_front_overlay": True,
                    "has_top_overlay": True,
                    "has_active_variant": True,
                    "has_emissive": True
                },
                ...
            }
        """
        if self._machines_cache is not None:
            return self._machines_cache
        
        machines: Dict[str, Dict[str, bool]] = {}
        
        # Scan for machines/{machine_name}/overlay_*.png patterns
        overlay_pattern = re.compile(
            r"assets/gregtech/textures/blocks/machines/([^/]+)/overlay_([^_]+)(_active)?(_emissive)?\.png"
        )
        
        for resource_path in self.resource_manager.resource_index.keys():
            match = overlay_pattern.match(resource_path)
            if match:
                machine_name = match.group(1)
                face = match.group(2)  # front, top, side, etc.
                is_active = match.group(3) is not None
                is_emissive = match.group(4) is not None
                
                # Initialize machine entry if not exists
                if machine_name not in machines:
                    machines[machine_name] = {
                        "has_front_overlay": False,
                        "has_top_overlay": False,
                        "has_side_overlay": False,
                        "has_active_variant": False,
                        "has_emissive": False,
                    }
                
                # Update capabilities
                if face == "front":
                    machines[machine_name]["has_front_overlay"] = True
                elif face == "top":
                    machines[machine_name]["has_top_overlay"] = True
                elif face == "side":
                    machines[machine_name]["has_side_overlay"] = True
                
                if is_active:
                    machines[machine_name]["has_active_variant"] = True
                if is_emissive:
                    machines[machine_name]["has_emissive"] = True
        
        self._machines_cache = machines
        return machines
    
    def discover_voltage_tiers(self) -> Set[str]:
        """
        Discover available voltage tiers by scanning casing textures.
        
        Returns:
            Set of tier names (lv, mv, hv, ev, iv, luv, zpm, uv, uhv, etc.)
        """
        if self._voltage_tiers_cache is not None:
            return self._voltage_tiers_cache
        
        tiers = set()
        
        # Scan for casings/voltage/{tier}/ patterns
        casing_pattern = re.compile(
            r"assets/gregtech/textures/blocks/casings/voltage/([^/]+)/"
        )
        
        for resource_path in self.resource_manager.resource_index.keys():
            match = casing_pattern.match(resource_path)
            if match:
                tier_name = match.group(1).lower()
                tiers.add(tier_name)
        
        self._voltage_tiers_cache = tiers
        return tiers
    
    def is_gregtech_block(self, block_id: str) -> bool:
        """
        Check if a block ID belongs to GregTech.
        
        Args:
            block_id: Block identifier (e.g., "gregtech:machine")
        
        Returns:
            True if block is from GregTech
        """
        return block_id.startswith("gregtech:")
    
    def get_machine_info(self, machine_name: str) -> Optional[Dict[str, bool]]:
        """
        Get capabilities info for a specific machine.
        
        Args:
            machine_name: Machine identifier
        
        Returns:
            Dict of capabilities or None if not found
        """
        machines = self.discover_machines()
        return machines.get(machine_name)
    
    def list_available_materials(self) -> List[str]:
        """
        Get sorted list of available materials.
        
        Returns:
            Sorted list of material names
        """
        return sorted(self.discover_materials())
    
    def list_available_tiers(self) -> List[str]:
        """
        Get sorted list of available voltage tiers.
        
        Returns:
            Sorted list of tier names
        """
        return sorted(self.discover_voltage_tiers())
    
    def list_available_machines(self) -> List[str]:
        """
        Get sorted list of available machines.
        
        Returns:
            Sorted list of machine names
        """
        machines = self.discover_machines()
        return sorted(machines.keys())
    
    def analyze_machine_variants(
        self, machine_name: str
    ) -> List[Tuple[str, bool, bool]]:
        """
        Analyze all rendering variants for a machine.
        
        Args:
            machine_name: Machine identifier
        
        Returns:
            List of (tier, active, has_emissive) tuples
        """
        info = self.get_machine_info(machine_name)
        if not info:
            return []
        
        tiers = self.list_available_tiers()
        variants = []
        
        for tier in tiers:
            # Base variant (inactive)
            variants.append((tier, False, False))
            
            # Active variant if supported
            if info["has_active_variant"]:
                variants.append((tier, True, info["has_emissive"]))
        
        return variants
    
    def clear_cache(self):
        """Clear all cached discovery results."""
        self._materials_cache = None
        self._material_sets_cache = None
        self._machines_cache = None
        self._voltage_tiers_cache = None
