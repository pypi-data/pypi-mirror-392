import click
from sqlblocks.core.assembler import SQLAssembler
from sqlblocks.plugins.folder_plugin import FolderPlugin
from dataclasses import fields
from pathlib import Path


@click.group()
def cli():
    """SQL Dependency Manager - manage SQL blocks with dependencies"""
    pass

@cli.command()
@click.argument('path')
def install(path):
    """Install SQL blocks from a directory"""
    manager = "SQLManager()"
    try:
        manager.install_blocks(path)
        click.echo(f"✓ Blocks installed from {path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()

@cli.command()
def build():
    current_dir = Path.cwd()
    assembler = SQLAssembler(sql_loader = FolderPlugin(current_dir / "sql_blocks"))
    assembler.build()
      
@cli.command()
@click.argument('name')
def assembly(name):
    current_dir = Path.cwd()
    assembler = SQLAssembler()
    print(assembler.assemble_sql(name))