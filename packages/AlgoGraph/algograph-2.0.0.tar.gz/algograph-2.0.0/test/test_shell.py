"""
Tests for AlgoGraph shell commands.
"""

import pytest
import tempfile
import os
from AlgoGraph import Graph, Vertex, Edge, save_graph, load_graph
from AlgoGraph.shell import GraphContext, GraphShell
from AlgoGraph.shell.commands import (
    PwdCommand, LsCommand, CdCommand, InfoCommand,
    NeighborsCommand, FindCommand, PathCommand, ShortestCommand,
    ComponentsCommand, BfsCommand, SaveCommand
)


@pytest.fixture
def simple_graph():
    """Create a simple graph for testing."""
    vertices = {Vertex('A'), Vertex('B'), Vertex('C'), Vertex('D')}
    edges = {
        Edge('A', 'B', directed=False),
        Edge('B', 'C', directed=False),
        Edge('A', 'D', directed=False)
    }
    return Graph(vertices, edges)


@pytest.fixture
def weighted_graph():
    """Create a weighted graph for testing."""
    vertices = {Vertex('A'), Vertex('B'), Vertex('C')}
    edges = {
        Edge('A', 'B', weight=2.0),
        Edge('B', 'C', weight=3.0),
        Edge('A', 'C', weight=10.0)
    }
    return Graph(vertices, edges)


@pytest.fixture
def attributed_graph():
    """Create a graph with vertex attributes."""
    vertices = {
        Vertex('Alice', attrs={'age': 30, 'city': 'NYC'}),
        Vertex('Bob', attrs={'age': 25, 'city': 'Boston'}),
    }
    edges = {Edge('Alice', 'Bob', directed=False)}
    return Graph(vertices, edges)


class TestPwdCommand:
    """Tests for pwd command."""

    def test_pwd_at_root(self, simple_graph):
        """Test pwd at root."""
        ctx = GraphContext(simple_graph)
        cmd = PwdCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert result.output == "/"

    def test_pwd_at_vertex(self, simple_graph):
        """Test pwd at a vertex."""
        ctx = GraphContext(simple_graph, 'A')
        cmd = PwdCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert result.output == "/A"

    def test_pwd_in_neighbors_mode(self, simple_graph):
        """Test pwd in neighbors mode."""
        ctx = GraphContext(simple_graph, 'A', mode='neighbors')
        cmd = PwdCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert result.output == "/A/neighbors"


class TestLsCommand:
    """Tests for ls command."""

    def test_ls_at_root(self, simple_graph):
        """Test ls at root shows all vertices."""
        ctx = GraphContext(simple_graph)
        cmd = LsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'A/' in result.output
        assert 'B/' in result.output
        assert 'C/' in result.output
        assert 'D/' in result.output

    def test_ls_at_vertex(self, attributed_graph):
        """Test ls at vertex shows attributes and neighbors."""
        ctx = GraphContext(attributed_graph, 'Alice')
        cmd = LsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'age = 30' in result.output
        assert 'city = NYC' in result.output
        assert 'neighbors/' in result.output

    def test_ls_in_neighbors_mode(self, simple_graph):
        """Test ls in neighbors mode shows neighbors."""
        ctx = GraphContext(simple_graph, 'A', mode='neighbors')
        cmd = LsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'B/' in result.output
        assert 'D/' in result.output


class TestCdCommand:
    """Tests for cd command."""

    def test_cd_to_root(self, simple_graph):
        """Test cd to root."""
        ctx = GraphContext(simple_graph, 'A')
        cmd = CdCommand()
        result = cmd.execute(ctx, ['/'])

        assert result.success
        assert result.context.current_vertex is None

    def test_cd_to_vertex(self, simple_graph):
        """Test cd to a vertex."""
        ctx = GraphContext(simple_graph)
        cmd = CdCommand()
        result = cmd.execute(ctx, ['A'])

        assert result.success
        assert result.context.current_vertex == 'A'

    def test_cd_to_neighbors(self, simple_graph):
        """Test cd to neighbors mode."""
        ctx = GraphContext(simple_graph, 'A')
        cmd = CdCommand()
        result = cmd.execute(ctx, ['neighbors'])

        assert result.success
        assert result.context.is_in_neighbors_mode()

    def test_cd_dotdot_from_vertex(self, simple_graph):
        """Test cd .. from vertex."""
        ctx = GraphContext(simple_graph, 'A')
        cmd = CdCommand()
        result = cmd.execute(ctx, ['..'])

        assert result.success
        assert result.context.current_vertex is None

    def test_cd_dotdot_from_neighbors(self, simple_graph):
        """Test cd .. from neighbors mode."""
        ctx = GraphContext(simple_graph, 'A', mode='neighbors')
        cmd = CdCommand()
        result = cmd.execute(ctx, ['..'])

        assert result.success
        assert result.context.current_vertex == 'A'
        assert not result.context.is_in_neighbors_mode()

    def test_cd_to_neighbor_from_neighbors_mode(self, simple_graph):
        """Test cd to neighbor from neighbors mode."""
        ctx = GraphContext(simple_graph, 'A', mode='neighbors')
        cmd = CdCommand()
        result = cmd.execute(ctx, ['B'])

        assert result.success
        assert result.context.current_vertex == 'B'
        assert not result.context.is_in_neighbors_mode()

    def test_cd_to_nonexistent_vertex(self, simple_graph):
        """Test cd to nonexistent vertex."""
        ctx = GraphContext(simple_graph)
        cmd = CdCommand()
        result = cmd.execute(ctx, ['Z'])

        assert not result.success
        assert 'not found' in result.error.lower()


class TestInfoCommand:
    """Tests for info command."""

    def test_info_at_root(self, simple_graph):
        """Test info at root shows graph info."""
        ctx = GraphContext(simple_graph)
        cmd = InfoCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'Vertices: 4' in result.output
        assert 'Edges: 3' in result.output

    def test_info_at_vertex(self, attributed_graph):
        """Test info at vertex shows vertex info."""
        ctx = GraphContext(attributed_graph, 'Alice')
        cmd = InfoCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'Vertex: Alice' in result.output
        assert 'age = 30' in result.output


class TestNeighborsCommand:
    """Tests for neighbors command."""

    def test_neighbors_of_vertex(self, simple_graph):
        """Test showing neighbors of a vertex."""
        ctx = GraphContext(simple_graph, 'A')
        cmd = NeighborsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'B' in result.output
        assert 'D' in result.output

    def test_neighbors_at_root(self, simple_graph):
        """Test neighbors at root fails."""
        ctx = GraphContext(simple_graph)
        cmd = NeighborsCommand()
        result = cmd.execute(ctx, [])

        assert not result.success


class TestFindCommand:
    """Tests for find command."""

    def test_find_existing_vertex(self, attributed_graph):
        """Test finding an existing vertex."""
        ctx = GraphContext(attributed_graph)
        cmd = FindCommand()
        result = cmd.execute(ctx, ['Alice'])

        assert result.success
        assert 'Alice' in result.output
        assert 'age = 30' in result.output

    def test_find_nonexistent_vertex(self, simple_graph):
        """Test finding nonexistent vertex."""
        ctx = GraphContext(simple_graph)
        cmd = FindCommand()
        result = cmd.execute(ctx, ['Z'])

        assert not result.success
        assert 'not found' in result.error.lower()


class TestPathCommand:
    """Tests for path command."""

    def test_path_exists(self, simple_graph):
        """Test finding a path that exists."""
        ctx = GraphContext(simple_graph)
        cmd = PathCommand()
        result = cmd.execute(ctx, ['A', 'C'])

        assert result.success
        assert 'A' in result.output
        assert 'C' in result.output

    def test_path_not_exists(self, simple_graph):
        """Test finding a path that doesn't exist."""
        # Add isolated vertex
        graph = simple_graph.add_vertex(Vertex('Z'))
        ctx = GraphContext(graph)
        cmd = PathCommand()
        result = cmd.execute(ctx, ['A', 'Z'])

        assert result.success
        assert 'No path' in result.output


class TestShortestCommand:
    """Tests for shortest path command."""

    def test_shortest_path(self, weighted_graph):
        """Test finding shortest path."""
        ctx = GraphContext(weighted_graph)
        cmd = ShortestCommand()
        result = cmd.execute(ctx, ['A', 'C'])

        assert result.success
        # Should find A -> B -> C (distance 5) not A -> C (distance 10)
        assert 'Distance: 5.0' in result.output


class TestComponentsCommand:
    """Tests for components command."""

    def test_single_component(self, simple_graph):
        """Test graph with single connected component."""
        ctx = GraphContext(simple_graph)
        cmd = ComponentsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'Connected components: 1' in result.output

    def test_multiple_components(self, simple_graph):
        """Test graph with multiple components."""
        # Add isolated vertex
        graph = simple_graph.add_vertex(Vertex('Z'))
        ctx = GraphContext(graph)
        cmd = ComponentsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'Connected components: 2' in result.output


class TestBfsCommand:
    """Tests for BFS command."""

    def test_bfs_from_vertex(self, simple_graph):
        """Test BFS from a vertex."""
        ctx = GraphContext(simple_graph, 'A')
        cmd = BfsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'BFS from A' in result.output
        assert 'Visited 4 vertices' in result.output

    def test_bfs_with_explicit_start(self, simple_graph):
        """Test BFS with explicit start vertex."""
        ctx = GraphContext(simple_graph)
        cmd = BfsCommand()
        result = cmd.execute(ctx, ['A'])

        assert result.success
        assert 'BFS from A' in result.output


class TestGraphShell:
    """Tests for GraphShell integration."""

    def test_shell_execution(self, simple_graph):
        """Test executing commands in shell."""
        ctx = GraphContext(simple_graph)
        shell = GraphShell(ctx)

        # Execute cd
        result = shell.execute_command('cd A')
        assert result
        assert shell.context.current_vertex == 'A'

        # Execute ls
        result = shell.execute_command('ls')
        assert result

        # Execute pwd
        result = shell.execute_command('pwd')
        assert result

    def test_shell_unknown_command(self, simple_graph):
        """Test unknown command handling."""
        ctx = GraphContext(simple_graph)
        shell = GraphShell(ctx)

        result = shell.execute_command('invalid_command')
        assert result  # Should continue execution

    def test_shell_exit(self, simple_graph):
        """Test exit command."""
        ctx = GraphContext(simple_graph)
        shell = GraphShell(ctx)

        result = shell.execute_command('exit')
        assert not result  # Should stop execution


class TestSerialization:
    """Tests for graph serialization."""

    def test_save_and_load_graph(self, attributed_graph):
        """Test saving and loading a graph."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name

        try:
            # Save graph
            save_graph(attributed_graph, filename)

            # Load graph
            loaded = load_graph(filename)

            # Verify
            assert loaded.vertex_count == attributed_graph.vertex_count
            assert loaded.edge_count == attributed_graph.edge_count

            # Check vertices
            alice = loaded.get_vertex('Alice')
            assert alice is not None
            assert alice.attrs['age'] == 30
            assert alice.attrs['city'] == 'NYC'

            bob = loaded.get_vertex('Bob')
            assert bob is not None
            assert bob.attrs['age'] == 25

            # Check edge
            assert loaded.has_edge('Alice', 'Bob')

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_save_weighted_graph(self, weighted_graph):
        """Test saving and loading weighted graph."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name

        try:
            save_graph(weighted_graph, filename)
            loaded = load_graph(filename)

            # Check edge weights
            edge_ab = loaded.get_edge('A', 'B')
            assert edge_ab is not None
            assert edge_ab.weight == 2.0

            edge_bc = loaded.get_edge('B', 'C')
            assert edge_bc is not None
            assert edge_bc.weight == 3.0

        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestSaveCommand:
    """Tests for save command."""

    def test_save_command(self, simple_graph):
        """Test save command saves the graph."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name

        try:
            ctx = GraphContext(simple_graph)
            cmd = SaveCommand()
            result = cmd.execute(ctx, [filename])

            assert result.success
            assert os.path.exists(filename)

            # Verify we can load it back
            loaded = load_graph(filename)
            assert loaded.vertex_count == simple_graph.vertex_count
            assert loaded.edge_count == simple_graph.edge_count

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_save_command_no_args(self, simple_graph):
        """Test save command without filename."""
        ctx = GraphContext(simple_graph)
        cmd = SaveCommand()
        result = cmd.execute(ctx, [])

        assert not result.success
        assert 'Usage' in result.error


class TestAbsolutePaths:
    """Tests for absolute path navigation."""

    def test_cd_absolute_path(self, simple_graph):
        """Test cd with absolute path."""
        # Start at root
        ctx = GraphContext(simple_graph)
        cmd = CdCommand()

        # Navigate to A with absolute path
        result = cmd.execute(ctx, ['/A'])

        assert result.success
        assert result.context.current_vertex == 'A'

    def test_cd_absolute_path_from_vertex(self, simple_graph):
        """Test cd with absolute path from another vertex."""
        # Start at B
        ctx = GraphContext(simple_graph, 'B')
        cmd = CdCommand()

        # Navigate to D with absolute path
        result = cmd.execute(ctx, ['/D'])

        assert result.success
        assert result.context.current_vertex == 'D'

    def test_cd_absolute_path_nonexistent(self, simple_graph):
        """Test cd with absolute path to nonexistent vertex."""
        ctx = GraphContext(simple_graph)
        cmd = CdCommand()

        result = cmd.execute(ctx, ['/Z'])

        assert not result.success
        assert 'not found' in result.error.lower()


class TestQuotedVertexNames:
    """Tests for vertex names with spaces."""

    def test_vertex_with_spaces(self):
        """Test navigating to vertex with spaces in name."""
        vertices = {Vertex('Alice Smith'), Vertex('Bob Jones')}
        edges = {Edge('Alice Smith', 'Bob Jones', directed=False)}
        graph = Graph(vertices, edges)

        ctx = GraphContext(graph)
        cmd = CdCommand()

        # This should work with shlex parsing
        result = cmd.execute(ctx, ['Alice Smith'])

        assert result.success
        assert result.context.current_vertex == 'Alice Smith'

    def test_ls_with_space_names(self):
        """Test ls with vertex names containing spaces."""
        vertices = {Vertex('Alice Smith'), Vertex('Bob Jones')}
        edges = set()
        graph = Graph(vertices, edges)

        ctx = GraphContext(graph)
        cmd = LsCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert 'Alice Smith' in result.output
        assert 'Bob Jones' in result.output
