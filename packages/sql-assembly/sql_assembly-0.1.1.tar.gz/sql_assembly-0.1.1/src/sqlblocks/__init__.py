"""
SQLBlocks - for convenient work with ready-made SQL blocks
"""
__version__ = "0.1.1"

from sqlblocks.core.entities import BasicSQLBlock
from sqlblocks.core.registry import SQLBlockRegistry
from sqlblocks.core.assembler import SQLAssembler
from sqlblocks.plugins import BasicSQLScriptLoader