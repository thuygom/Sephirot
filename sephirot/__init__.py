"""Sephirot: spec-first dual knowledge graph builder."""

from .ambiguity import score_spec
from .builder import build_dual_tree

__all__ = ["build_dual_tree", "score_spec"]
