"""
SQLBlocks - for convenient work with ready-made SQL blocks
"""
__version__ = "0.1.0"

from core.entities import BasicSQLBlock
from sqlblocks.core.registry import SQLBlockRegistry
from core.assembler import SQLAssembler
from plugins import BasicSQLScriptLoader