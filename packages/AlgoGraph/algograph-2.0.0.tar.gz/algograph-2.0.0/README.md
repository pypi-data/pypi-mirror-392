# AlgoGraph

Independent graph data structures and algorithms library with optional AlgoTree integration.

## Overview

AlgoGraph provides immutable graph data structures with a clean, functional API. It works standalone and optionally integrates with AlgoTree for seamless interoperability between tree and graph representations.

## Key Features

- **Immutable by default**: All operations return new graph objects
- **Type-safe**: Full type hints for IDE support
- **Directed and undirected**: Support for both edge types
- **Weighted edges**: Built-in support for edge weights
- **Attributes**: Both vertices and edges can carry arbitrary attributes
- **Interoperability**: Convert between trees (AlgoTree) and graphs (AlgoGraph)
- **Interactive shell**: VFS-like interface for graph exploration
- **Comprehensive algorithms**: 56+ graph algorithms across 8 categories
- **Fluent builder API**: Construct graphs with 82% less code
- **Research-based**: Algorithms from peer-reviewed literature

## Core Classes

### Vertex

Immutable graph vertex with attributes:

```python
from AlgoGraph import Vertex

# Create vertex
v = Vertex('A', attrs={'value': 10, 'color': 'red'})

# Immutable updates
v2 = v.with_attrs(value=20)
v3 = v.without_attrs('color')
```

### Edge

Immutable edge connecting two vertices:

```python
from AlgoGraph import Edge

# Directed edge with weight
e1 = Edge('A', 'B', directed=True, weight=5.0)

# Undirected edge
e2 = Edge('A', 'C', directed=False)

# With attributes
e3 = Edge('B', 'C', weight=3.0, attrs={'label': 'highway'})

# Immutable updates
e4 = e1.with_weight(10.0)
e5 = e1.reversed()  # B -> A
```

### Graph

Immutable graph container:

```python
from AlgoGraph import Graph, Vertex, Edge

# Build graph
v1, v2, v3 = Vertex('A'), Vertex('B'), Vertex('C')
e1 = Edge('A', 'B', weight=2.0)
e2 = Edge('B', 'C', weight=3.0)

g = Graph({v1, v2, v3}, {e1, e2})

# Query graph
g.has_vertex('A')          # True
g.has_edge('A', 'B')       # True
g.degree('A')              # 1
g.neighbors('B')           # {'C'}

# Immutable updates
g2 = g.add_vertex(Vertex('D'))
g3 = g.add_edge(Edge('C', 'D'))
g4 = g.remove_vertex('A')
```

## Interoperability with AlgoTree (Optional)

**Note**: The interop functions require AlgoTree to be installed or available in PYTHONPATH.

Convert between trees and graphs seamlessly:

```python
from AlgoTree import Node, Tree
from AlgoGraph import tree_to_graph, graph_to_tree

# Tree to Graph
tree = Tree(Node('root',
    Node('child1', Node('grandchild')),
    Node('child2')
))

graph = tree_to_graph(tree)
# Graph with 4 vertices, 3 edges (root->child1, root->child2, child1->grandchild)

# Graph to Tree (extracts spanning tree)
recovered_tree = graph_to_tree(graph, 'root')
```

### Flat Dictionary Format

Both AlgoTree and AlgoGraph support a flat dictionary interchange format:

```python
from AlgoGraph import graph_to_flat_dict, flat_dict_to_graph

# Graph to flat dict
flat = graph_to_flat_dict(graph)
# {
#     'root': {'.name': 'root', '.edges': [{'target': 'child1', ...}], ...},
#     'child1': {'.name': 'child1', '.edges': [...], ...},
#     ...
# }

# Flat dict to graph
recovered = flat_dict_to_graph(flat)
```

This format is compatible with AlgoTree's flat exporter, enabling easy data exchange.

## Graph Algorithms

AlgoGraph includes common graph algorithms (in `algorithms/` module):

### Traversal

```python
from AlgoGraph.algorithms import dfs, bfs, topological_sort

# Depth-first search
visited = dfs(graph, start_vertex='A')

# Breadth-first search
levels = bfs(graph, start_vertex='A')

# Topological sort (DAG only)
ordered = topological_sort(graph)
```

### Shortest Paths

```python
from AlgoGraph.algorithms import dijkstra, bellman_ford, floyd_warshall

# Single-source shortest path (Dijkstra)
distances = dijkstra(graph, source='A')

# With negative weights (Bellman-Ford)
distances = bellman_ford(graph, source='A')

# All-pairs shortest paths
dist_matrix = floyd_warshall(graph)
```

### Connectivity

```python
from AlgoGraph.algorithms import (
    connected_components,
    strongly_connected_components,
    is_connected,
    is_bipartite
)

# Connected components (undirected)
components = connected_components(graph)

# Strongly connected components (directed)
scc = strongly_connected_components(graph)

# Check connectivity
if is_connected(graph):
    print("Graph is connected")

# Check bipartiteness
is_bip, coloring = is_bipartite(graph)
```

### Spanning Trees

```python
from AlgoGraph.algorithms import minimum_spanning_tree, kruskal, prim

# Minimum spanning tree
mst = minimum_spanning_tree(graph)  # Uses Kruskal by default
mst = kruskal(graph)
mst = prim(graph, start='A')
```

### Centrality (NEW in v1.3.0)

```python
from AlgoGraph.algorithms import (
    pagerank, betweenness_centrality, closeness_centrality
)

# Find influencers with PageRank
pr = pagerank(social_network)
top_influencer = max(pr, key=pr.get)

# Find bridge people with betweenness
bc = betweenness_centrality(network)
top_broker = max(bc, key=bc.get)

# Find central nodes with closeness
cc = closeness_centrality(network)
```

### Flow Networks (NEW in v1.3.0)

```python
from AlgoGraph.algorithms import max_flow, min_cut

# Maximum flow from source to sink
flow_value = max_flow(network, 'Source', 'Sink')

# Find bottleneck (minimum cut)
cut_value, source_set, sink_set = min_cut(network, 'Source', 'Sink')
```

### Matching (NEW in v1.3.0)

```python
from AlgoGraph.algorithms import hopcroft_karp, is_perfect_matching

# Maximum bipartite matching (job assignment)
workers = {'Alice', 'Bob', 'Charlie'}
jobs = {'Backend', 'Frontend', 'DevOps'}
matching = hopcroft_karp(assignments, workers, jobs)

# Check if everyone can be matched
if is_perfect_matching(assignments, workers, jobs):
    print("Everyone gets a job!")
```

### Graph Coloring (NEW in v1.3.0)

```python
from AlgoGraph.algorithms import welsh_powell, chromatic_number

# Exam scheduling (minimize time slots)
conflicts = build_conflict_graph(exams)
coloring = welsh_powell(conflicts)
num_slots = chromatic_number(conflicts)
print(f"Need {num_slots} exam time slots")
```

## Design Philosophy

AlgoGraph follows the same design principles as AlgoTree:

1. **Immutability**: All operations return new objects
2. **Composability**: Operations chain naturally
3. **Functional style**: Prefer pure functions
4. **Type safety**: Full type hints
5. **Clean separation**: Data structures vs algorithms

## Use Cases

- **Network analysis**: Social networks, computer networks
- **Route planning**: Transportation, logistics
- **Dependency graphs**: Build systems, package managers
- **State machines**: Workflow, game logic
- **Knowledge graphs**: Semantic networks, ontologies
- **Tree structures**: When you need bidirectional navigation (use AlgoGraph), unidirectional parent-child (use AlgoTree)

## When to Use AlgoGraph vs AlgoTree

| Use AlgoGraph when... | Use AlgoTree when... |
|----------------------|---------------------|
| You have cycles in your structure | Your structure is acyclic (tree) |
| You need bidirectional edges | Parent-child is sufficient |
| Working with networks/graphs | Working with hierarchies |
| Need to track edge weights/labels | Edges are just relationships |
| Multiple paths between nodes | Single path between any two nodes |

## Examples

### Social Network

```python
from AlgoGraph import Graph, Vertex, Edge

# Create people
alice = Vertex('Alice', attrs={'age': 30})
bob = Vertex('Bob', attrs={'age': 25})
charlie = Vertex('Charlie', attrs={'age': 35})

# Create friendships (undirected)
friend1 = Edge('Alice', 'Bob', directed=False)
friend2 = Edge('Bob', 'Charlie', directed=False)

# Build network
network = Graph(
    {alice, bob, charlie},
    {friend1, friend2}
)

# Query network
bobs_friends = network.neighbors('Bob')
# {'Alice', 'Charlie'}
```

### Road Network

```python
# Cities
cities = {
    Vertex('NYC', attrs={'population': 8000000}),
    Vertex('Boston', attrs={'population': 700000}),
    Vertex('DC', attrs={'population': 700000})
}

# Roads with distances
roads = {
    Edge('NYC', 'Boston', weight=215.0, attrs={'highway': 'I-95'}),
    Edge('NYC', 'DC', weight=225.0, attrs={'highway': 'I-95'}),
    Edge('Boston', 'DC', weight=440.0)
}

road_network = Graph(cities, roads)

# Find shortest route
from AlgoGraph.algorithms import dijkstra
distances = dijkstra(road_network, 'NYC')
print(f"NYC to DC: {distances['DC']} miles")
```

### Dependency Graph

```python
# Build dependencies
packages = {Vertex(name) for name in ['app', 'lib1', 'lib2', 'utils']}
deps = {
    Edge('app', 'lib1'),
    Edge('app', 'lib2'),
    Edge('lib1', 'utils'),
    Edge('lib2', 'utils')
}

dep_graph = Graph(packages, deps)

# Get build order
from AlgoGraph.algorithms import topological_sort
build_order = topological_sort(dep_graph)
# ['utils', 'lib1', 'lib2', 'app'] or ['utils', 'lib2', 'lib1', 'app']
```

## Installation

AlgoGraph is an independent library that can be used standalone:

```bash
# For development (when in released/ directory)
export PYTHONPATH=/path/to/released:$PYTHONPATH
```

```python
# Use AlgoGraph standalone
from AlgoGraph import Graph, Vertex, Edge
from AlgoGraph.algorithms import dijkstra, bfs

# For interop features, also add AlgoTree to PYTHONPATH
export PYTHONPATH=/path/to/released:$PYTHONPATH
from AlgoTree import Node, Tree
from AlgoGraph import tree_to_graph, graph_to_tree
```

**Package structure:**
```
released/
├── AlgoTree/      # Tree data structures
└── AlgoGraph/     # Graph data structures (this library)
```

AlgoGraph works independently but provides optional interop with AlgoTree when both are available.

## Interactive Shell

AlgoGraph includes an interactive shell for exploring graphs with a filesystem-like interface.

### Quick Start

```bash
cd /home/spinoza/github/released
export PYTHONPATH=.
python -m AlgoGraph.shell.shell
```

### Example Session

```bash
graph(5v):/$ ls
Alice/  [2 neighbors]
Bob/    [3 neighbors]
Charlie/  [2 neighbors]

graph(5v):/$ cd Alice
Now at: /Alice

graph(5v):/Alice$ ls
Attributes:
  age = 30
  city = NYC

neighbors/  [2 vertices]

graph(5v):/Alice$ cd neighbors
Now at: /Alice/neighbors

graph(5v):/Alice/neighbors$ ls
Bob/  <->
Charlie/  <->

graph(5v):/Alice/neighbors$ cd Bob
Now at: /Bob

graph(5v):/Bob$ path Alice Eve
Path found: Alice -> Bob -> Diana -> Eve
Length: 3 edges
```

### Navigation Model

The shell treats graphs like a filesystem:
- `/` - Graph root (lists all vertices)
- `/vertex_id` - At a specific vertex (shows attributes + neighbors/)
- `/vertex_id/neighbors` - Viewing neighbors you can navigate to

### Available Commands

**Navigation:**
- `cd <vertex>` - Navigate to a vertex
- `cd neighbors` - View neighbors of current vertex
- `cd ..` - Go up one level
- `ls` - List contents
- `pwd` - Print current path

**Information:**
- `info` - Show graph or vertex information
- `neighbors` - Show neighbors of current vertex
- `find <vertex>` - Find a vertex

**Graph Queries:**
- `path <v1> <v2>` - Find path between vertices
- `shortest <v1> <v2>` - Find shortest path
- `components` - Show connected components
- `bfs [start]` - Breadth-first search

See [shell/README.md](shell/README.md) for complete documentation.

## Future Enhancements

Potential additions:

- More graph algorithms (matching, flow, coloring)
- Graph visualization export (GraphViz, etc.)
- Serialization formats (JSON, GraphML, etc.)
- Performance optimizations for large graphs
- Shell enhancements (graph modification, bookmarks, history)

## Related Projects

- **AlgoTree**: Tree data structures and algorithms
- **NetworkX**: Comprehensive Python graph library (mutable)
- **graph-tool**: High-performance graph analysis

## License

Same as AlgoTree (see main repository LICENSE file).
