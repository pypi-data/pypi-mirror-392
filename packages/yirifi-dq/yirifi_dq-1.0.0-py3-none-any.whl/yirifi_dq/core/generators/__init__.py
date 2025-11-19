"""
Generators module for creating and managing data generation utilities.

Available utilities:
- slugs: AI-enhanced slug generation and deduplication
"""

from .slugs import SlugGenerator, generate_slug_for_collection

__all__ = ["SlugGenerator", "generate_slug_for_collection"]
