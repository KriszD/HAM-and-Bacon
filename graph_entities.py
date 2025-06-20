"""HAM and Bacon - graph_entities.py

Contains Graph and Vertex classes, as well as methods for dealing with Graph and Vertex data.

This file is Copyright (c) 2025 Skye Mah-Madjar, Krisztian Drimba, Joshua Iaboni, and Xiayu Lyu."""

from __future__ import annotations
from collections import deque
from typing import Any
from random import choice


class _Vertex:
    """A vertex in a book review graph, used to represent a user or a book.

    Each vertex item is either an actor or movie.

    Instance Attributes:
        - item: The data stored in this vertex, representing an actor or movie.
        - kind: The type of this vertex: 'actor' or 'movie'.
        - neighbours: The vertices that are adjacent to this vertex.
        - appearances: The set of movies this actor appears in (if kind == 'actor')
        - sim_score: How similar the movie is to a certain movie in the graph, determined by the
        similarity score algorithm (if kind == 'movie')
        - movie_info: A tuple storing a movie's release year, number of votes, and rating

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'movie', 'actor'}
        - self.sim_score <= 1
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]
    appearances: set[str]
    sim_score: float
    movie_info: tuple[int, int, float]  # (year, votes, rating)

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'actor', 'movie'}
            - self.appearences == set() or kind == 'actor'
            - self.sim_score == 0 or kind == 'movie'
            - self.movie_info == (0,0,0) or kind == 'movie'
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()
        self.appearances = set()
        self.sim_score = 0
        self.movie_info = (0, 0, 0)


class Graph:
    """A graph used to represent a network of actors/movies.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'actor', 'movie'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'actor', 'movie'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def get_vertices(self) -> dict:
        """Return the dictionary of vertices in the graph."""
        return self._vertices

    def add_appearances(self, actor: str, movie: str) -> None:
        """Adds a movie the actor has appeared in to a set.
        Raise a ValueError if actor does not appear as a vertex in this graph."""
        if actor in self._vertices:
            self._vertices[actor].appearances.add(movie)
        else:
            raise ValueError

    def add_sim_score(self, movie: str, sim_scores: dict) -> None:
        """Adds a movie's similarity score from a given dictionary.

        Preconditions:
        - movie in sim_scores
        """

        sim_score = sim_scores[movie]
        self._vertices[movie].sim_score = sim_score

    def item_in_graph(self, item: str) -> bool:
        """Returns whether the given item appears as a vertex in this graph."""
        return item in self._vertices

    def get_common_movies(self, item1: str, item2: str) -> set:
        """Returns the movie(s) that are in common between two actors

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        >>> g = Graph()
        >>> g.add_vertex('actor1', kind = 'actor')
        >>> g.add_vertex('actor2', kind = 'actor')
        >>> g.add_appearances('actor1','movie1')
        >>> g.add_appearances('actor1','movie2')
        >>> g.add_appearances('actor2','movie3')
        >>> g.add_appearances('actor2','movie2')
        >>> g.add_appearances('actor2','movie1')
        >>> actual = g.get_common_movies('actor1','actor2')
        >>> expected = {'movie2','movie1'}
        >>> actual == expected
        True
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            return v1.appearances.intersection(v2.appearances)
        else:
            raise ValueError

    def get_appearances(self, actor: str) -> set:
        """Returns a set of movies an actor has appeared in

        Preconditions:
        - actor in self._vertices
        """
        return self._vertices[actor].appearances

    def get_random_item(self) -> Any:
        """Returns the item of a random vertex

        Preconditions:
        - self._vertices != {}
        """
        vertices_copy = set(self._vertices.keys())
        vertices_copy_tup = tuple(vertices_copy)
        return choice(vertices_copy_tup)

    ####################################################################################################################
    # BFS (Breadth First Search)
    ####################################################################################################################

    def shortest_path_bfs(self, starting_item: str, target_item: str) -> str | list[Any]:
        """Find the shortest path between two actors using BFS.

        Raise a ValueError if starting_item or target_item do not appear as vertices in this graph.

        >>> g = Graph()
        >>> g.add_vertex('actor1', kind = 'actor')
        >>> g.add_vertex('actor2', kind = 'actor')
        >>> g.add_vertex('actor3', kind = 'actor')
        >>> g.add_vertex('actor4', kind = 'actor')
        >>> g.add_edge('actor1','actor2')
        >>> g.add_edge('actor2','actor3')
        >>> g.add_edge('actor2','actor4')
        >>> g.add_edge('actor3','actor4')
        >>> actural = g.shortest_path_bfs('actor1','actor4')
        >>> expected = ['actor1','actor2','actor4']
        >>> actural == expected
        True
        """
        if starting_item not in self._vertices or target_item not in self._vertices:
            raise ValueError

        queue = deque([(starting_item, [starting_item])])
        visited = {starting_item}

        while queue:
            current_actor, path = queue.popleft()

            if current_actor == target_item:
                return path

            for neighbour in self._vertices[current_actor].neighbours:
                if neighbour.item not in visited:
                    visited.add(neighbour.item)
                    queue.append((neighbour.item, path + [neighbour.item]))

        return []

    def shortest_path_bfs_filtered(self, items: tuple[str, str], key: str,
                                   thresholds: tuple[float, float], movies: dict) -> str | list[Any]:
        """Find the shortest path between two actors using BFS where actors can only be included in the path
        if they match the filtering requirements.

        Raise a ValueError if starting_item or target_item do not appear as vertices in this graph.
        """
        lower, upper = thresholds[0], thresholds[1]
        starting_item, target_item = items[0], items[1]
        if starting_item not in self._vertices or target_item not in self._vertices:
            raise ValueError("One or both actors are not in the graph.")

        queue = deque([(starting_item, [starting_item])])
        visited = {starting_item}

        while queue:
            current_actor, path = queue.popleft()

            if current_actor == target_item:
                return path

            for neighbour in self._vertices[current_actor].neighbours:
                if neighbour.item not in visited:
                    is_valid, _ = self.filter_by_key((current_actor, neighbour.item),
                                                     key, (lower, upper), movies)
                    self._sp_bfs_filtered_helper(is_valid, visited, neighbour.item, (queue, path))
                    # if is_valid:
                    #     visited.add(neighbour.item)
                    #     queue.append((neighbour.item, path + [neighbour.item]))

        return []

    @staticmethod
    def _sp_bfs_filtered_helper(is_valid: bool, visited: set, item: Any,
                                queue_path: tuple[deque, list[str]]) -> None:
        """A helper function for shortest_path_bfs_filtered
        If is valid_is True, adds item to visited and appends (item, path + [item]) to queue."""
        queue = queue_path[0]
        path = queue_path[1]
        if is_valid:
            visited.add(item)
            queue.append((item, path + [item]))

    def shortest_distance_bfs(self, starting_item: str) -> dict[Any, float]:
        """Compute the shortest distance from a given actor to all other actors using BFS.
        Raise a ValueError if starting_item does not appear as vertices in this graph.

        >>> g = Graph()
        >>> g.add_vertex('actor1', kind = 'actor')
        >>> g.add_vertex('actor2', kind = 'actor')
        >>> g.add_vertex('actor3', kind = 'actor')
        >>> g.add_vertex('actor4', kind = 'actor')
        >>> g.add_vertex('movie1', kind = 'movie')
        >>> g.add_vertex('movie2', kind = 'movie')
        >>> g.add_vertex('movie3', kind = 'movie')
        >>> g.add_edge('actor1','movie1')
        >>> g.add_edge('actor1','movie2')
        >>> g.add_edge('actor2','movie2')
        >>> g.add_edge('actor2','movie3')
        >>> g.add_edge('actor3','movie3')
        >>> g.add_edge('actor3','movie1')
        >>> g.add_edge('actor4','movie3')
        >>> movies = {'movie1': [[], [1970, [], 2.0]], 'movie2': [[], [1980, [], 1.0]], 'movie3': [[], \
         [1990, [], 2.5]], 'movie4': [[], [1991, [], 3.0]]}
        >>> actual = g.shortest_distance_bfs('actor1')
        >>> expected = {'actor2':2, 'actor3':2, 'actor4':4, 'movie1':1, 'movie2':1, 'movie3':3}
        >>> actual == expected
        True

        """
        if starting_item not in self._vertices:
            raise ValueError

        distances = {actor: float("inf") for actor in self._vertices}
        distances[starting_item] = 0

        queue = deque([starting_item])
        visited = {starting_item}

        while queue:
            current_actor = queue.popleft()

            for neighbour in self._vertices[current_actor].neighbours:
                if neighbour.item != starting_item and neighbour.item not in visited:
                    visited.add(neighbour.item)
                    distances[neighbour.item] = distances[current_actor] + 1
                    queue.append(neighbour.item)

        # Remove the starting actor
        return {actor: dist for actor, dist in distances.items() if actor != starting_item}

    def filter_by_key(self, actors: tuple[str, str], key: str,
                      thresholds: tuple[float, float], movies: dict) -> tuple[bool, set[str]] | None:
        """Checks if two actors have a movie connecting them that matches the given filter.

        Raise a KeyError if key is not 'release date' or 'rating'.

        Raise a ValueError if actor1 or actor2 do not appear as vertices in this graph.

        Preconditions:
        - key in {'release date', 'rating'}

        >>> g = Graph()
        >>> g.add_vertex('actor1', kind = 'actor')
        >>> g.add_vertex('actor2', kind = 'actor')
        >>> g.add_vertex('actor3', kind = 'actor')
        >>> g.add_vertex('actor4', kind = 'actor')
        >>> g.add_vertex('movie1', kind = 'movie')
        >>> g.add_vertex('movie2', kind = 'movie')
        >>> g.add_vertex('movie3', kind = 'movie')
        >>> g.add_edge('actor1','movie1')
        >>> g.add_edge('actor1','movie2')
        >>> g.add_edge('actor2','movie2')
        >>> g.add_edge('actor2','movie3')
        >>> g.add_edge('actor3','movie3')
        >>> g.add_edge('actor3','movie1')
        >>> g.add_edge('actor4','movie3')
        >>> g.add_appearances('actor1','movie1')
        >>> g.add_appearances('actor1','movie2')
        >>> g.add_appearances('actor2','movie2')
        >>> g.add_appearances('actor2','movie3')
        >>> g.add_appearances('actor3','movie3')
        >>> g.add_appearances('actor3','movie1')
        >>> g.add_appearances('actor4','movie3')
        >>> test_movies = {'movie1': [[], [1970, [], 2.0]], 'movie2': [[], [1980, [], 1.0]], \
         'movie3': [[], [1990, [], 2.5]], 'movie4': [[], [1991, [], 3.0]]}
        >>> test1 = g.filter_by_key(('actor1', 'actor2'), 'rating', (1985, 1991), test_movies)
        >>> test2 = g.filter_by_key(('actor1', 'actor2'), 'release date', (1965, 1991), test_movies)
        >>> test3 = g.filter_by_key(('actor3', 'actor4'), 'rating', (2.0, 3), test_movies)
        >>> test4 = g.filter_by_key(('actor1', 'actor3'), 'rating', (2.5, 3), test_movies)
        >>> test1 == (False, set())
        True
        >>> test2 == (True, {'movie2'})
        True
        >>> test3 == (True, {'movie3'})
        True
        >>> test4 == (False, set())
        True
        """
        lower, upper = thresholds[0], thresholds[1]
        actor1, actor2 = actors[0], actors[1]
        if actor1 in self._vertices and actor2 in self._vertices:
            v1 = self._vertices[actor1]
            v2 = self._vertices[actor2]

            if key == 'release date':
                common = v1.appearances.intersection(v2.appearances)
                common_filtered = {movie for movie in common if lower <= float(movies[movie][1][0]) <= upper}
                if common_filtered:
                    return True, common_filtered

            elif key == 'rating':
                common = v1.appearances.intersection(v2.appearances)
                common_filtered = {movie for movie in common if lower <= float(movies[movie][1][2]) <= upper}
                if common_filtered:
                    return True, common_filtered

            else:
                raise KeyError

        else:
            raise ValueError

        return False, set()


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['collections', 'random'],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
