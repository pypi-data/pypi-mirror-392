"""
TexForge - Forge Perfect LaTeX Papers

Automated LaTeX paper compilation, validation, and maintenance.
Forge your research with precision and ease.
"""

__version__ = "0.1.1"
__author__ = "Jue Xu"
__description__ = "Forge perfect LaTeX papers with automated tools"

# Make key classes available at package level
from .config import PaperMaintenanceConfig
from .pdf_compiler import PDFCompiler, CompilationResult
from .notifications import NotificationManager

__all__ = [
    "PaperMaintenanceConfig",
    "PDFCompiler",
    "CompilationResult",
    "NotificationManager",
]
