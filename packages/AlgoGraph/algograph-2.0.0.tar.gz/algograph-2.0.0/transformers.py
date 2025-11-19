"""
Composable transformation system for graphs.

This module provides a clean, functional approach to graph transformations
that can be composed using the pipe operator |.

Inspired by AlgoTree's transformer pattern, adapted for graph-specific operations.
"""

from typing import Any, Callable, Optional, Union, List, Dict, Set, TypeVar, Generic, Tuple
from abc import ABC, abstractmethod
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AlgoGraph.graph import Graph
from AlgoGraph.vertex import Vertex
from AlgoGraph.edge import Edge

T = TypeVar('T')
S = TypeVar('S')


class Transformer(ABC, Generic[T, S]):
    """
    Base class for composable graph transformations.

    Transformers can be composed using the pipe operator |.
    They enable functional-style graph processing pipelines.

    Example:
        >>> from AlgoGraph import Graph
        >>> from AlgoGraph.transformers import filter_vertices, to_dict
        >>> result = graph | filter_vertices(lambda v: v.get('active')) | to_dict()
    """

    @abstractmethod
    def __call__(self, input_data: T) -> S:
        """
        Apply transformation to input.

        Args:
            input_data: Input to transform

        Returns:
            Transformed output
        """
        pass

    def __ror__(self, other: T) -> S:
        """
        Enable pipe syntax: graph | transformer.

        This is called when transformer appears on the right side of |.
        """
        return self(other)

    def __or__(self, other: 'Transformer[S, Any]') -> 'Pipeline':
        """
        Compose transformers: transformer1 | transformer2.

        Creates a pipeline that applies transformers sequentially.
        """
        return Pipeline(self, other)

    def when(self, condition: Callable[[T], bool]) -> 'ConditionalTransformer[T, S]':
        """
        Apply transformer only if condition is met.

        Args:
            condition: Predicate function

        Returns:
            Conditional transformer

        Example:
            >>> large_only = filter_edges(...).when(lambda g: g.edge_count > 100)
        """
        return ConditionalTransformer(self, condition)

    def debug(self, name: str = "", callback: Optional[Callable[[Any], None]] = None) -> 'DebugTransformer':
        """
        Add debugging output to transformer.

        Args:
            name: Name for debug output
            callback: Optional callback for custom debug handling

        Returns:
            Debug-wrapped transformer
        """
        return DebugTransformer(self, name, callback)


class Pipeline(Transformer[T, Any]):
    """
    Sequential composition of transformers.

    Applies transformers left-to-right in a pipeline.
    """

    def __init__(self, *transformers: Transformer):
        """
        Create pipeline from transformers.

        Args:
            *transformers: Transformers to apply in sequence
        """
        self.transformers = transformers

    def __call__(self, input_data: T) -> Any:
        """Apply all transformers in sequence."""
        result = input_data
        for transformer in self.transformers:
            result = transformer(result)
        return result

    def __repr__(self) -> str:
        return f"Pipeline({', '.join(repr(t) for t in self.transformers)})"


class ConditionalTransformer(Transformer[T, Union[S, T]]):
    """
    Applies transformer only if condition is met.

    If condition fails, returns input unchanged.
    """

    def __init__(self, transformer: Transformer[T, S], condition: Callable[[T], bool]):
        """
        Create conditional transformer.

        Args:
            transformer: Transformer to apply conditionally
            condition: Predicate determining whether to apply
        """
        self.transformer = transformer
        self.condition = condition

    def __call__(self, input_data: T) -> Union[S, T]:
        """Apply transformer if condition is true, else return input."""
        if self.condition(input_data):
            return self.transformer(input_data)
        return input_data

    def __repr__(self) -> str:
        return f"ConditionalTransformer({self.transformer}, {self.condition})"


class DebugTransformer(Transformer[T, T]):
    """
    Wraps transformer with debug output.

    Prints or logs transformation for debugging pipelines.
    """

    def __init__(
        self,
        transformer: Transformer[T, T],
        name: str = "",
        callback: Optional[Callable[[Any], None]] = None
    ):
        """
        Create debug wrapper.

        Args:
            transformer: Transformer to wrap
            name: Name for debug output
            callback: Optional callback for custom debug handling
        """
        self.transformer = transformer
        self.name = name
        self.callback = callback

    def __call__(self, input_data: T) -> T:
        """Apply transformer with debug output."""
        print(f"[DEBUG {self.name}] Input: {type(input_data).__name__}")
        result = self.transformer(input_data)
        print(f"[DEBUG {self.name}] Output: {type(result).__name__}")

        if self.callback:
            self.callback(result)

        return result

    def __repr__(self) -> str:
        return f"DebugTransformer({self.transformer}, name={self.name!r})"


# Graph -> Graph transformers (closed transformations)

class GraphTransformer(Transformer[Graph, Graph]):
    """Base class for graph-to-graph transformations."""
    pass


class FilterVerticesTransformer(GraphTransformer):
    """
    Filter graph vertices by predicate.

    Removes vertices (and incident edges) that don't match predicate.
    """

    def __init__(self, predicate: Callable[[Vertex], bool]):
        """
        Create vertex filter.

        Args:
            predicate: Function returning True for vertices to keep
        """
        self.predicate = predicate

    def __call__(self, graph: Graph) -> Graph:
        """Apply filter to graph."""
        matching_ids = {v.id for v in graph.vertices if self.predicate(v)}
        return graph.subgraph(matching_ids)

    def __repr__(self) -> str:
        return f"FilterVerticesTransformer({self.predicate})"


class FilterEdgesTransformer(GraphTransformer):
    """
    Filter graph edges by predicate.

    Removes edges that don't match predicate.
    """

    def __init__(self, predicate: Callable[[Edge], bool]):
        """
        Create edge filter.

        Args:
            predicate: Function returning True for edges to keep
        """
        self.predicate = predicate

    def __call__(self, graph: Graph) -> Graph:
        """Apply filter to graph."""
        filtered_edges = {e for e in graph.edges if self.predicate(e)}
        return Graph(graph.vertices, filtered_edges)

    def __repr__(self) -> str:
        return f"FilterEdgesTransformer({self.predicate})"


class MapVerticesTransformer(GraphTransformer):
    """
    Map function over all vertices.

    Applies transformation function to each vertex, preserving structure.
    """

    def __init__(self, fn: Callable[[Vertex], Vertex]):
        """
        Create vertex mapper.

        Args:
            fn: Function to transform each vertex
        """
        self.fn = fn

    def __call__(self, graph: Graph) -> Graph:
        """Apply mapping to all vertices."""
        new_vertices = {self.fn(v) for v in graph.vertices}
        return Graph(new_vertices, graph.edges)

    def __repr__(self) -> str:
        return f"MapVerticesTransformer({self.fn})"


class MapEdgesTransformer(GraphTransformer):
    """
    Map function over all edges.

    Applies transformation function to each edge, preserving structure.
    """

    def __init__(self, fn: Callable[[Edge], Edge]):
        """
        Create edge mapper.

        Args:
            fn: Function to transform each edge
        """
        self.fn = fn

    def __call__(self, graph: Graph) -> Graph:
        """Apply mapping to all edges."""
        new_edges = {self.fn(e) for e in graph.edges}
        return Graph(graph.vertices, new_edges)

    def __repr__(self) -> str:
        return f"MapEdgesTransformer({self.fn})"


class SubgraphTransformer(GraphTransformer):
    """
    Extract subgraph by vertex IDs.

    Creates subgraph containing only specified vertices and their edges.
    """

    def __init__(self, vertex_ids: Union[Set[str], List[str], Callable[[Graph], Set[str]]]):
        """
        Create subgraph extractor.

        Args:
            vertex_ids: Set of vertex IDs or function returning vertex IDs
        """
        self.vertex_ids = vertex_ids

    def __call__(self, graph: Graph) -> Graph:
        """Extract subgraph."""
        if callable(self.vertex_ids):
            ids = self.vertex_ids(graph)
        else:
            ids = set(self.vertex_ids) if isinstance(self.vertex_ids, list) else self.vertex_ids

        return graph.subgraph(ids)

    def __repr__(self) -> str:
        return f"SubgraphTransformer({self.vertex_ids})"


class ReverseTransformer(GraphTransformer):
    """
    Reverse all directed edges in graph.

    Undirected edges remain unchanged.
    """

    def __call__(self, graph: Graph) -> Graph:
        """Reverse all edges."""
        reversed_edges = {e.reversed() if e.directed else e for e in graph.edges}
        return Graph(graph.vertices, reversed_edges)

    def __repr__(self) -> str:
        return "ReverseTransformer()"


class UndirectedTransformer(GraphTransformer):
    """
    Convert all edges to undirected.

    Makes a directed graph undirected.
    """

    def __call__(self, graph: Graph) -> Graph:
        """Convert to undirected."""
        undirected_edges = {Edge(e.source, e.target, directed=False, weight=e.weight, attrs=e.attrs)
                           for e in graph.edges}
        return Graph(graph.vertices, undirected_edges)

    def __repr__(self) -> str:
        return "UndirectedTransformer()"


# Algorithm-based transformers

class LargestComponentTransformer(GraphTransformer):
    """
    Extract largest connected component.

    For directed graphs, uses strongly connected components.
    """

    def __call__(self, graph: Graph) -> Graph:
        """Extract largest component."""
        from AlgoGraph.algorithms import connected_components, strongly_connected_components

        if graph.is_directed:
            components = strongly_connected_components(graph)
        else:
            components = connected_components(graph)

        if not components:
            return Graph()

        largest = max(components, key=len)
        return graph.subgraph(largest)

    def __repr__(self) -> str:
        return "LargestComponentTransformer()"


class MinimumSpanningTreeTransformer(GraphTransformer):
    """
    Extract minimum spanning tree.

    Uses Kruskal's algorithm.
    """

    def __call__(self, graph: Graph) -> Graph:
        """Extract MST."""
        from AlgoGraph.algorithms import minimum_spanning_tree
        return minimum_spanning_tree(graph)

    def __repr__(self) -> str:
        return "MinimumSpanningTreeTransformer()"


# Graph -> Other transformers (open transformations)

class ToDictTransformer(Transformer[Graph, Dict[str, Any]]):
    """
    Convert graph to dictionary representation.

    Returns dict with vertices and edges as lists.
    """

    def __call__(self, graph: Graph) -> Dict[str, Any]:
        """Convert to dict."""
        return {
            'vertices': [{'id': v.id, 'attrs': v.attrs} for v in graph.vertices],
            'edges': [
                {
                    'source': e.source,
                    'target': e.target,
                    'directed': e.directed,
                    'weight': e.weight,
                    'attrs': e.attrs
                }
                for e in graph.edges
            ]
        }

    def __repr__(self) -> str:
        return "ToDictTransformer()"


class ToAdjacencyListTransformer(Transformer[Graph, Dict[str, List[str]]]):
    """
    Convert graph to adjacency list representation.

    Returns dict mapping vertex ID to list of neighbor IDs.
    """

    def __call__(self, graph: Graph) -> Dict[str, List[str]]:
        """Convert to adjacency list."""
        adj_list = {v.id: list(graph.neighbors(v.id)) for v in graph.vertices}
        return adj_list

    def __repr__(self) -> str:
        return "ToAdjacencyListTransformer()"


class StatsTransformer(Transformer[Graph, Dict[str, Any]]):
    """
    Compute graph statistics.

    Returns dict with vertex count, edge count, density, etc.
    """

    def __call__(self, graph: Graph) -> Dict[str, Any]:
        """Compute statistics."""
        v_count = graph.vertex_count
        e_count = graph.edge_count

        # Graph density
        if v_count > 1:
            max_edges = v_count * (v_count - 1)
            if not graph.is_directed:
                max_edges //= 2
            density = e_count / max_edges if max_edges > 0 else 0.0
        else:
            density = 0.0

        # Degree statistics
        degrees = [graph.degree(v.id) for v in graph.vertices]
        avg_degree = sum(degrees) / v_count if v_count > 0 else 0.0
        max_degree = max(degrees) if degrees else 0
        min_degree = min(degrees) if degrees else 0

        return {
            'vertex_count': v_count,
            'edge_count': e_count,
            'density': density,
            'avg_degree': avg_degree,
            'max_degree': max_degree,
            'min_degree': min_degree,
            'is_directed': graph.is_directed,
        }

    def __repr__(self) -> str:
        return "StatsTransformer()"


# Convenience factory functions

def filter_vertices(predicate: Callable[[Vertex], bool]) -> FilterVerticesTransformer:
    """
    Create vertex filter transformer.

    Args:
        predicate: Function returning True for vertices to keep

    Returns:
        FilterVerticesTransformer instance

    Example:
        >>> result = graph | filter_vertices(lambda v: v.get('active'))
    """
    return FilterVerticesTransformer(predicate)


def filter_edges(predicate: Callable[[Edge], bool]) -> FilterEdgesTransformer:
    """
    Create edge filter transformer.

    Args:
        predicate: Function returning True for edges to keep

    Returns:
        FilterEdgesTransformer instance

    Example:
        >>> result = graph | filter_edges(lambda e: e.weight > 5.0)
    """
    return FilterEdgesTransformer(predicate)


def map_vertices(fn: Callable[[Vertex], Vertex]) -> MapVerticesTransformer:
    """
    Create vertex mapper transformer.

    Args:
        fn: Function to transform each vertex

    Returns:
        MapVerticesTransformer instance

    Example:
        >>> result = graph | map_vertices(lambda v: v.with_attrs(processed=True))
    """
    return MapVerticesTransformer(fn)


def map_edges(fn: Callable[[Edge], Edge]) -> MapEdgesTransformer:
    """
    Create edge mapper transformer.

    Args:
        fn: Function to transform each edge

    Returns:
        MapEdgesTransformer instance

    Example:
        >>> result = graph | map_edges(lambda e: e.with_weight(e.weight * 2))
    """
    return MapEdgesTransformer(fn)


def subgraph(vertex_ids: Union[Set[str], List[str], Callable[[Graph], Set[str]]]) -> SubgraphTransformer:
    """
    Create subgraph extractor transformer.

    Args:
        vertex_ids: Set of vertex IDs or function returning vertex IDs

    Returns:
        SubgraphTransformer instance

    Example:
        >>> result = graph | subgraph({'A', 'B', 'C'})
    """
    return SubgraphTransformer(vertex_ids)


def reverse() -> ReverseTransformer:
    """
    Create edge reversal transformer.

    Returns:
        ReverseTransformer instance

    Example:
        >>> result = graph | reverse()
    """
    return ReverseTransformer()


def to_undirected() -> UndirectedTransformer:
    """
    Create undirected conversion transformer.

    Returns:
        UndirectedTransformer instance

    Example:
        >>> result = directed_graph | to_undirected()
    """
    return UndirectedTransformer()


def largest_component() -> LargestComponentTransformer:
    """
    Create largest component extractor transformer.

    Returns:
        LargestComponentTransformer instance

    Example:
        >>> result = graph | largest_component()
    """
    return LargestComponentTransformer()


def minimum_spanning_tree() -> MinimumSpanningTreeTransformer:
    """
    Create MST extractor transformer.

    Returns:
        MinimumSpanningTreeTransformer instance

    Example:
        >>> result = weighted_graph | minimum_spanning_tree()
    """
    return MinimumSpanningTreeTransformer()


def to_dict() -> ToDictTransformer:
    """
    Create dict converter transformer.

    Returns:
        ToDictTransformer instance

    Example:
        >>> result = graph | to_dict()
    """
    return ToDictTransformer()


def to_adjacency_list() -> ToAdjacencyListTransformer:
    """
    Create adjacency list converter transformer.

    Returns:
        ToAdjacencyListTransformer instance

    Example:
        >>> adj_list = graph | to_adjacency_list()
    """
    return ToAdjacencyListTransformer()


def stats() -> StatsTransformer:
    """
    Create statistics calculator transformer.

    Returns:
        StatsTransformer instance

    Example:
        >>> statistics = graph | stats()
    """
    return StatsTransformer()
