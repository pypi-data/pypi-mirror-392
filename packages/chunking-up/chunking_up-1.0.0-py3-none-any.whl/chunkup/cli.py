"""CHONK from your terminal! 🦛"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import time
import sys
from pathlib import Path

from .core.chunker import CHONK, ChonkConfig
from .utils.constants import MASCOT, CHONK_SPEED

console = Console()

@click.group()
@click.version_option(version="1.0.0", prog_name="chunkup")
def main():
    """CHUNKUP 🦛 - CHONK your documents at the speed of light!"""
    pass

@main.command()
@click.argument("content")
@click.option("--strategy", default="recursive", help="CHONKING strategy",
              type=click.Choice(["recursive", "semantic", "token", "markdown", "html", "code", "pdf"]))
@click.option("--size", default=512, help="Chunk size in tokens/characters")
@click.option("--overlap", default=50, help="Chunk overlap")
@click.option("--embed/--no-embed", default=False, help="Generate embeddings")
@click.option("--vector-db", help="Vector DB to ship to (pinecone, qdrant, weaviate, chroma)")
@click.option("--refine/--no-refine", default=True, help="Refine chunks")
@click.option("--language", help="Language code (auto-detect if not specified)")
@click.option("--output", "-o", help="Output file for chunks (JSON)")
@click.option("--verbose/--quiet", default=False, help="Verbose output")
def chonk(content: str, strategy: str, size: int, overlap: int, embed: bool,
          vector_db: str, refine: bool, language: str, output: str, verbose: bool):
    """CHONK content from file, URL, or text 🦛⚡"""

    if verbose:
        console.print(MASCOT, style="bold magenta")

    # Validate inputs
    if not content:
        console.print("❌ No content provided!", style="red")
        sys.exit(1)

    # Build config
    config = ChonkConfig(
        chunk_size=size,
        chunk_overlap=overlap,
        strategy=strategy,
        embed=embed,
        vector_db=vector_db,
        refine=refine,
    )

    chonker = CHONK(config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:

        task = progress.add_task(f"[cyan]CHONKING with {strategy}...", total=None)

        start_time = time.perf_counter()

        try:
            result = chonker.chonk(content)
        except Exception as e:
            console.print(f"❌ CHONK failed: {e}", style="red")
            sys.exit(1)

        duration = time.perf_counter() - start_time

        progress.update(task, completed=True)

    # Success message
    console.print(f"\n✅ CHONKED into {len(result.chunks)} chunks in {duration:.3f}s!", style="green bold")

    if vector_db:
        console.print(f"🚢 Shipped to {vector_db}!", style="blue bold")

    # Display summary
    _display_summary(result, strategy, verbose)

    # Save output if requested
    if output:
        _save_output(result, output, console)

    # Show preview
    if verbose and result.chunks:
        _display_preview(result, console)

@main.command()
@click.option("--provider", default="openai", help="Embedding provider",
              type=click.Choice(["openai", "cohere", "huggingface", "vertex"]))
@click.option("--model", help="Model name")
def test_embed(provider: str, model: str):
    """Test embeddings with CHONK 🧠"""

    console.print(f"🧠 Testing {provider} embeddings...", style="blue")

    from .core.embedder import Embedder

    try:
        embedder = Embedder(provider=provider, model=model)
        chunks = ["Hello world", "CHONK is life", "Pygmy hippos are cute"]

        embeddings = embedder.embed(chunks)

        console.print(f"✅ Generated {len(embeddings)} embeddings", style="green")
        console.print(f"📊 Embedding dimension: {len(embeddings[0])}", style="cyan")

    except Exception as e:
        console.print(f"❌ Embedding test failed: {e}", style="red")
        sys.exit(1)

@main.command()
@click.argument("vector_db", type=click.Choice(["pinecone", "qdrant", "weaviate", "chroma"]))
def test_vector(vector_db: str):
    """Test vector DB connection 🔌"""

    console.print(f"🔌 Testing {vector_db} connection...", style="blue")

    try:
        from .core.shipper import VectorShipper

        shipper = VectorShipper(vector_db)

        # Test with dummy data
        chunks = [{"metadata": {"test": True}}]
        embeddings = [[0.1] * 1536]  # Dummy embedding

        ids = shipper.ship(chunks, embeddings)

        console.print(f"✅ Successfully shipped to {vector_db}", style="green")
        console.print(f"📦 Vector IDs: {ids[:3]}...", style="cyan")

    except Exception as e:
        console.print(f"❌ Vector DB test failed: {e}", style="red")
        sys.exit(1)

@main.command()
def languages():
    """Show all supported languages 🌍"""

    from .utils.languages import get_all_supported_languages, LANGUAGE_CODES

    table = Table(title="Supported Languages")
    table.add_column("Code", style="cyan")
    table.add_column("Language", style="green")

    for code in get_all_supported_languages()[:20]:  # Show first 20
        table.add_row(code, LANGUAGE_CODES.get(code, "Unknown"))

    console.print(table)
    console.print(f"... and {len(get_all_supported_languages()) - 20} more languages!")

def _display_summary(result, strategy: str, verbose: bool):
    """Display CHONK summary"""
    table = Table(title="CHONK Summary", style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Strategy", strategy)
    table.add_row("Chunks", str(len(result.chunks)))
    table.add_row("Language", result.metadata.get("language", "unknown"))
    table.add_row("Refined", "✅" if result.config.refine else "❌")
    table.add_row("Embedded", "✅" if result.config.embed else "❌")
    table.add_row("Speed", CHONK_SPEED)

    console.print(table)

def _save_output(result, output: str, console: Console):
    """Save chunks to file"""
    import json

    try:
        data = {
            "chunks": result.chunks,
            "metadata": result.metadata,
            "vector_ids": result.vector_ids,
        }

        Path(output).write_text(json.dumps(data, indent=2))
        console.print(f"💾 Saved to {output}", style="green")

    except Exception as e:
        console.print(f"❌ Failed to save: {e}", style="red")

def _display_preview(result, console: Console):
    """Display first few chunks"""
    console.print("\n[bold]First CHONK Preview:[/bold]", style="yellow")

    for i, chunk in enumerate(result.chunks[:3]):
        content = chunk.get("content", "")
        preview = content[:100] + "..." if len(content) > 100 else content

        panel = Panel(
            Text(preview, style="white"),
            title=f"Chunk {i+1}",
            border_style="blue"
        )
        console.print(panel)