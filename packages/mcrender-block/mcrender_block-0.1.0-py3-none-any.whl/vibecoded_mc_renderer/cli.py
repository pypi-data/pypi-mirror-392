"""CLI interface for the Minecraft block renderer."""

from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track

from vibecoded_mc_renderer.core.resource_manager import ResourceManager
from vibecoded_mc_renderer.core.model_loader import ModelLoader
from vibecoded_mc_renderer.core.texture_manager import TextureManager
from vibecoded_mc_renderer.core.renderer import BlockRenderer
from vibecoded_mc_renderer.core.gregtech_analyzer import GregTechAnalyzer
from vibecoded_mc_renderer.rendering.machine_renderer import MachineRenderer

app = typer.Typer(
    name="mcrender",
    help="CLI tool for rendering Minecraft blocks from jar files",
    add_completion=False,
)
console = Console()


@app.command()
def render(
    jar_file: Path = typer.Argument(..., help="Path to Minecraft jar file", exists=True),
    block_id: str = typer.Argument(..., help="Block ID (e.g., 'minecraft:stone')"),
    output: Path = typer.Option("output.png", "--output", "-o", help="Output file path"),
    size: int = typer.Option(128, "--size", "-s", help="Output image size (square)"),
    material: Optional[str] = typer.Option(None, "--material", "-m", help="Material for GregTech blocks (e.g., 'copper', 'steel')"),
    tier: Optional[str] = typer.Option(None, "--tier", "-t", help="Voltage tier for GregTech machines (e.g., 'lv', 'mv', 'hv')"),
    active: bool = typer.Option(False, "--active", "-a", help="Render GregTech machine in active state"),
) -> None:
    """Render a Minecraft block to an isometric image."""
    try:
        console.print(f"[cyan]Loading resources from {jar_file}...[/cyan]")

        with ResourceManager([jar_file]) as resource_manager:
            model_loader = ModelLoader(resource_manager)
            texture_manager = TextureManager(resource_manager)
            renderer = BlockRenderer(texture_manager)

            console.print(f"[cyan]Loading block model for '{block_id}'...[/cyan]")
            
            # Build properties for Forge blockstates if specified
            properties = {}
            if material:
                properties["material"] = material
            if tier:
                properties["tier"] = tier
            if active:
                properties["active"] = "true"
            
            model = model_loader.get_model_for_block(
                block_id, properties if properties else None
            )

            if model is None:
                console.print(f"[red]Error: Block '{block_id}' not found in jar file[/red]")
                raise typer.Exit(1)

            console.print(f"[cyan]Rendering block (size: {size}x{size})...[/cyan]")
            image = renderer.render_block(model, block_id, output_size=size)

            # Ensure output directory exists
            output.parent.mkdir(parents=True, exist_ok=True)

            image.save(output)
            console.print(f"[green]✓[/green] Saved to {output}")

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_blocks(
    jar_file: Path = typer.Argument(..., help="Path to Minecraft jar file", exists=True),
    namespace: Optional[str] = typer.Option(
        None, "--namespace", "-n", help="Filter by namespace (e.g., 'minecraft')"
    ),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of blocks to display"),
) -> None:
    """List all available blocks in the jar file."""
    try:
        console.print(f"[cyan]Loading resources from {jar_file}...[/cyan]")

        with ResourceManager([jar_file]) as resource_manager:
            blockstates = resource_manager.list_blockstates()

            if namespace:
                blockstates = [b for b in blockstates if b.startswith(f"{namespace}:")]

            total_count = len(blockstates)
            display_blocks = blockstates[:limit]

            # Create table
            table = Table(title=f"Available Blocks ({total_count} total)")
            table.add_column("Block ID", style="cyan")
            table.add_column("Namespace", style="magenta")

            for block_id in display_blocks:
                ns, name = block_id.split(":", 1)
                table.add_row(block_id, ns)

            console.print(table)

            if total_count > limit:
                console.print(
                    f"\n[yellow]Showing {limit} of {total_count} blocks. "
                    f"Use --limit to show more.[/yellow]"
                )

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def batch(
    jar_file: Path = typer.Argument(..., help="Path to Minecraft jar file", exists=True),
    blocks: Optional[str] = typer.Option(
        None, "--blocks", "-b", help="Comma-separated list of block IDs to render"
    ),
    output_dir: Path = typer.Option(
        "renders", "--output-dir", "-o", help="Output directory for rendered images"
    ),
    size: int = typer.Option(128, "--size", "-s", help="Output image size (square)"),
    namespace: Optional[str] = typer.Option(
        None, "--namespace", "-n", help="Render all blocks from a namespace"
    ),
) -> None:
    """Render multiple blocks in batch mode."""
    try:
        console.print(f"[cyan]Loading resources from {jar_file}...[/cyan]")

        with ResourceManager([jar_file]) as resource_manager:
            model_loader = ModelLoader(resource_manager)
            texture_manager = TextureManager(resource_manager)
            renderer = BlockRenderer(texture_manager)

            # Determine which blocks to render
            if blocks:
                block_list = [b.strip() for b in blocks.split(",")]
            elif namespace:
                all_blocks = resource_manager.list_blockstates()
                block_list = [b for b in all_blocks if b.startswith(f"{namespace}:")]
            else:
                console.print(
                    "[yellow]Please specify either --blocks or --namespace[/yellow]"
                )
                raise typer.Exit(1)

            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Render each block
            success_count = 0
            for block_id in track(block_list, description="Rendering blocks..."):
                try:
                    model = model_loader.get_model_for_block(block_id)
                    if model is None:
                        console.print(f"[yellow]⚠[/yellow] Skipping '{block_id}' (not found)")
                        continue

                    image = renderer.render_block(model, block_id, output_size=size)

                    # Generate filename from block ID
                    filename = block_id.replace(":", "_") + ".png"
                    output_path = output_dir / filename

                    image.save(output_path)
                    success_count += 1

                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Error rendering '{block_id}': {e}")
                    continue

            console.print(
                f"\n[green]✓[/green] Successfully rendered {success_count}/{len(block_list)} "
                f"blocks to {output_dir}"
            )

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info(
    jar_file: Path = typer.Argument(..., help="Path to Minecraft jar file", exists=True),
) -> None:
    """Display information about the jar file."""
    try:
        console.print(f"[cyan]Analyzing {jar_file}...[/cyan]")

        with ResourceManager([jar_file]) as resource_manager:
            namespaces = resource_manager.list_namespaces()
            blockstates = resource_manager.list_blockstates()

            # Count blocks per namespace
            namespace_counts = {}
            for block_id in blockstates:
                ns = block_id.split(":")[0]
                namespace_counts[ns] = namespace_counts.get(ns, 0) + 1

            # Create info table
            table = Table(title=f"Jar File Information: {jar_file.name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total Blocks", str(len(blockstates)))
            table.add_row("Namespaces", str(len(namespaces)))

            console.print(table)

            # Namespace breakdown
            if namespace_counts:
                console.print("\n[cyan]Blocks per Namespace:[/cyan]")
                for ns, count in sorted(
                    namespace_counts.items(), key=lambda x: x[1], reverse=True
                ):
                    console.print(f"  • {ns}: {count} blocks")

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def render_machine(
    jar_file: Path = typer.Argument(..., help="Path to GregTech jar file", exists=True),
    machine_name: str = typer.Argument(..., help="Machine name (e.g., 'electric_furnace')"),
    output: Path = typer.Option("machine.png", "--output", "-o", help="Output file path"),
    size: int = typer.Option(128, "--size", "-s", help="Output image size (square)"),
    tier: str = typer.Option("lv", "--tier", "-t", help="Voltage tier (lv, mv, hv, etc.)"),
    active: bool = typer.Option(False, "--active", "-a", help="Render in active state"),
    material: Optional[str] = typer.Option(None, "--material", "-m", help="Material override for casing color"),
    emissive_strength: float = typer.Option(1.0, "--emissive", "-e", help="Emissive glow strength (0.0-1.0)"),
    camera_height: float = typer.Option(1.5, "--camera-height", "-c", help="Camera angle (1.0=acute, 1.5=standard, 2.0=wide)"),
) -> None:
    """Render a GregTech machine with voltage tier and overlays."""
    try:
        console.print(f"[cyan]Loading GregTech resources from {jar_file}...[/cyan]")

        with ResourceManager([jar_file]) as resource_manager:
            texture_manager = TextureManager(resource_manager)
            machine_renderer = MachineRenderer(texture_manager, resource_manager)

            console.print(
                f"[cyan]Rendering machine '{machine_name}' (tier: {tier}, "
                f"active: {active}, size: {size}x{size})...[/cyan]"
            )
            
            image = machine_renderer.render_machine(
                machine_name=machine_name,
                tier=tier,
                active=active,
                material=material,
                output_size=size,
                emissive_strength=emissive_strength,
                camera_height=camera_height,
            )

            # Ensure output directory exists
            output.parent.mkdir(parents=True, exist_ok=True)

            image.save(output)
            console.print(f"[green]✓[/green] Saved to {output}")

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_gregtech(
    jar_file: Path = typer.Argument(..., help="Path to GregTech jar file", exists=True),
    resource_type: str = typer.Argument(
        ..., 
        help="Resource type to list: 'materials', 'tiers', 'machines', 'material-sets'"
    ),
) -> None:
    """List available GregTech resources (materials, tiers, machines, etc.)."""
    try:
        console.print(f"[cyan]Analyzing GregTech mod from {jar_file}...[/cyan]")

        with ResourceManager([jar_file]) as resource_manager:
            analyzer = GregTechAnalyzer(resource_manager)

            if resource_type == "materials":
                materials = analyzer.list_available_materials()
                table = Table(title=f"GregTech Materials ({len(materials)} total)")
                table.add_column("Material", style="cyan")
                
                for material in materials:
                    table.add_row(material)
                
                console.print(table)

            elif resource_type == "tiers":
                tiers = analyzer.list_available_tiers()
                table = Table(title=f"Voltage Tiers ({len(tiers)} total)")
                table.add_column("Tier", style="magenta")
                
                for tier in tiers:
                    table.add_row(tier)
                
                console.print(table)

            elif resource_type == "machines":
                machines = analyzer.discover_machines()
                table = Table(title=f"GregTech Machines ({len(machines)} total)")
                table.add_column("Machine", style="cyan")
                table.add_column("Front", style="green")
                table.add_column("Top", style="green")
                table.add_column("Active", style="yellow")
                table.add_column("Emissive", style="blue")
                
                for machine_name, info in sorted(machines.items()):
                    table.add_row(
                        machine_name,
                        "✓" if info["has_front_overlay"] else "✗",
                        "✓" if info["has_top_overlay"] else "✗",
                        "✓" if info["has_active_variant"] else "✗",
                        "✓" if info["has_emissive"] else "✗",
                    )
                
                console.print(table)

            elif resource_type == "material-sets":
                material_sets = sorted(analyzer.discover_material_sets())
                table = Table(title=f"Material Sets ({len(material_sets)} total)")
                table.add_column("Material Set", style="cyan")
                
                for material_set in material_sets:
                    table.add_row(material_set)
                
                console.print(table)

            else:
                console.print(
                    f"[red]Error: Unknown resource type '{resource_type}'[/red]\n"
                    "Valid types: materials, tiers, machines, material-sets"
                )
                raise typer.Exit(1)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)




# Temporary file with the new batch_gregtech command
# Copy this into cli.py before the "if __name__ == '__main__':" line

@app.command()
def batch_gregtech(
    jar_file: Path = typer.Argument(..., help="Path to GregTech jar file", exists=True),
    output_dir: Path = typer.Option("gregtech_renders", "--output-dir", "-o", help="Output directory"),
    render_type: str = typer.Option(
        "machines",
        "--type",
        "-t",
        help="What to render: machines, materials, cables, or all"
    ),
    tiers: Optional[str] = typer.Option(
        "lv,mv,hv",
        "--tiers",
        help="Comma-separated voltage tiers for machines (e.g., 'lv,mv,hv,ev')"
    ),
    materials: Optional[str] = typer.Option(
        None,
        "--materials",
        "-m",
        help="Comma-separated materials for material blocks (if not specified, renders all)"
    ),
    include_active: bool = typer.Option(
        False,
        "--include-active/--no-include-active",
        help="Include active state variants for machines (may fail for animated machines)"
    ),
    size: int = typer.Option(128, "--size", "-s", help="Output image size"),
) -> None:
    """Batch render GregTech machines, materials, or cables."""
    try:
        console.print(f"[cyan]Loading GregTech resources from {jar_file}...[/cyan]")
        
        with ResourceManager([jar_file]) as resource_manager:
            texture_manager = TextureManager(resource_manager)
            machine_renderer = MachineRenderer(texture_manager, resource_manager)
            analyzer = GregTechAnalyzer(resource_manager)
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            tier_list = [t.strip() for t in tiers.split(",")] if tiers else ["lv"]
            success_count = 0
            total_count = 0
            
            # Render machines
            if render_type in ["machines", "all"]:
                console.print("[cyan]Discovering machines...[/cyan]")
                machines = analyzer.list_available_machines()
                
                if not machines:
                    console.print("[yellow]No machines found in GregTech jar[/yellow]")
                else:
                    total_count += len(machines) * len(tier_list) * (2 if include_active else 1)
                    
                    for machine_name in track(machines, description="Rendering machines..."):
                        for tier in tier_list:
                            # Render inactive
                            try:
                                image = machine_renderer.render_machine(
                                    machine_name=machine_name,
                                    tier=tier,
                                    active=False,
                                    output_size=size,
                                )
                                output_path = output_dir / f"{machine_name}_{tier}.png"
                                image.save(output_path)
                                success_count += 1
                            except Exception as e:
                                console.print(f"[yellow]⚠[/yellow] Error rendering {machine_name} ({tier}): {e}")
                            
                            # Render active if requested
                            if include_active:
                                try:
                                    image = machine_renderer.render_machine(
                                        machine_name=machine_name,
                                        tier=tier,
                                        active=True,
                                        output_size=size,
                                    )
                                    output_path = output_dir / f"{machine_name}_{tier}_active.png"
                                    image.save(output_path)
                                    success_count += 1
                                except Exception as e:
                                    console.print(f"[yellow]⚠[/yellow] Error rendering {machine_name} ({tier}, active): {e}")
            
            # Render material blocks
            if render_type in ["materials", "all"]:
                console.print("[cyan]Discovering materials...[/cyan]")
                
                if materials:
                    material_list = [m.strip() for m in materials.split(",")]
                else:
                    material_list = analyzer.list_available_materials()[:50]  # Limit to first 50 if not specified
                
                if not material_list:
                    console.print("[yellow]No materials found[/yellow]")
                else:
                    total_count += len(material_list)
                    
                    for material in track(material_list, description="Rendering material blocks..."):
                        try:
                            image = machine_renderer.render_material_block(
                                material=material,
                                output_size=size,
                            )
                            output_path = output_dir / f"block_{material}.png"
                            image.save(output_path)
                            success_count += 1
                        except Exception as e:
                            console.print(f"[yellow]⚠[/yellow] Error rendering material block {material}: {e}")
            
            # Render cables
            if render_type in ["cables", "all"]:
                console.print("[cyan]Rendering cables...[/cyan]")
                
                cable_materials = ["copper", "gold", "aluminum", "platinum", "tungsten"] if not materials else [m.strip() for m in materials.split(",")]
                cable_sizes = ["single", "double", "quadruple"]
                
                total_count += len(cable_materials) * len(cable_sizes) * 2  # insulated + uninsulated
                
                for material in track(cable_materials, description="Rendering cables..."):
                    for cable_size in cable_sizes:
                        # Insulated
                        try:
                            image = machine_renderer.render_cable(
                                material=material,
                                size=cable_size,
                                insulated=True,
                                output_size=size,
                            )
                            output_path = output_dir / f"cable_{material}_{cable_size}_insulated.png"
                            image.save(output_path)
                            success_count += 1
                        except Exception as e:
                            console.print(f"[yellow]⚠[/yellow] Error rendering cable {material} {cable_size} (insulated): {e}")
                        
                        # Uninsulated
                        try:
                            image = machine_renderer.render_cable(
                                material=material,
                                size=cable_size,
                                insulated=False,
                                output_size=size,
                            )
                            output_path = output_dir / f"cable_{material}_{cable_size}_wire.png"
                            image.save(output_path)
                            success_count += 1
                        except Exception as e:
                            console.print(f"[yellow]⚠[/yellow] Error rendering cable {material} {cable_size} (wire): {e}")
            
            console.print(
                f"\n[green]✓[/green] Successfully rendered {success_count}/{total_count} items to {output_dir}"
            )

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
