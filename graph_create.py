"""HAM and Bacon - graph_create.py

This file contains functions for reading data from our datasets as well as functions for creating graphs/dictionaries
that store the processed information.

This file is Copyright (c) 2025 Skye Mah-Madjar, Krisztian Drimba, Joshua Iaboni, and Xiayu Lyu"""

from __future__ import annotations
import csv
from graph_entities import Graph


def initialize_graphs(dataset: str) -> tuple[Graph(), dict]:
    """Creates the actor graph and movies dictionary from the given dataset.
    actor_graph is a graph linking actors to actors using movies as the vertices
    movies is a dictionary with movie names as the keys and a tuple containing
    ({cast}, year, votes, rating) as the values"""

    movies = load_csv_file(dataset)
    actor_graph = create_actor_graph(movies)
    return actor_graph, movies


def load_csv_file(dataset: str) -> dict:
    """Loads data from a given csv file, creating a dictionary mapping each movie name to a tuple consisting of
    (1) a set of all actors in that movie and (2) a tuple containing the movie's
    release year, number of votes, and rating"""

    movies = {}
    with open(dataset, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row[1] not in movies:
                movies[row[1]] = ({row[0]}, (row[2], row[3], row[4]))  # Tuple containing ({cast}, year, votes, rating)
            else:
                movies[row[1]][0].add(row[0])
    return movies


def create_actor_graph(movies: dict) -> Graph:
    """Creates the actor graph.
    Each vertex in the graph is an actor, and each edge is every movie both actors have appeared in.
    Also adds the set of movies the actor has appeared in to the _Vertex object
    >>> movies = {'Movie1': ({'actor1', 'actor2'}, (1990, 200, 8.1)), 'Movie2': ({'actor1', 'actor4'}, (1990, 200, 6))}
    >>> actor_graph = create_actor_graph(movies)
    >>> actor1_neighbours = actor_graph.get_neighbours('actor1')
    >>> 'actor2' in actor1_neighbours and 'actor2' in actor1_neighbours
    True
    >>> actor1_appearances = actor_graph.get_appearances('actor1')
    >>> 'Movie1' in actor1_appearances and 'Movie2' in actor1_appearances
    True
    """
    graph = Graph()

    for movie in movies:
        for actor in movies[movie][0]:
            graph.add_vertex(actor, 'actor')
            graph.add_appearances(actor, movie)
            _create_actor_graph_helper(movies, movie, graph, actor)

    return graph


def _create_actor_graph_helper(movies: dict, movie: str, graph: Graph(), actor: str) -> None:
    """A helper function for create_actor_graph
    Adds edges between actor and actors in movies if the actors appear in the graph.
    """
    for actor2 in movies[movie][0]:
        if graph.item_in_graph(actor2) and actor != actor2:
            graph.add_edge(actor, actor2)


def create_recommended_movie_graph(main_movie: str, recommendations: list | dict, sim_scores: dict) -> Graph():
    """Creates a graph based on the movie recommendation list or reccomendation dictionary
    Each vertex in the graph is a movie, and each edge in the graph is the actors that appear in both movies
    Also adds each movie's cast, year, votes, and rating to the _Vertex object
    >>> recommendations = ['Shaun the Sheep Movie', 'Wild Romance', 'Shut Up and Shoot Me']
    >>> sim_scores = {'Shaun the Sheep Movie': 0.87, 'Wild Romance': 0.2, 'Shut Up and Shoot Me': 0.99}
    >>> main_movie = 'Ghost Stories'
    >>> rec_graph = create_recommended_movie_graph(main_movie, recommendations, sim_scores)
    >>> rec_graph.adjacent('Shaun the Sheep Movie', 'Ghost Stories')
    True
    >>> rec_graph.adjacent('Shaun the Sheep Movie', 'Wild Romance')
    False
    """

    graph = Graph()

    if isinstance(recommendations, dict):
        recommendations = list(recommendations.keys())

    graph.add_vertex(main_movie, 'movie')
    main_sim_score = {main_movie: 1}
    graph.add_sim_score(main_movie, main_sim_score)

    for movie in recommendations:
        graph.add_vertex(movie, 'movie')
        graph.add_sim_score(movie, sim_scores)
        graph.add_edge(movie, main_movie)

    return graph


def create_dict_from_csv(dataset: str) -> dict[str, float]:
    """Creates a dictionary from a CSV file."""
    actor_dict = {}

    with open(dataset, mode='r') as file:
        reader = csv.reader(file)

        next(reader)

        for row in reader:
            actor = row[0]
            rating = float(row[1])
            if rating != 'Infinity':
                actor_dict[actor] = rating

    sorted_actor_dict = dict(sorted(actor_dict.items(), key=lambda item: item[1]))

    return sorted_actor_dict


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['graph_entities', 'csv'],
        'allowed-io': ['load_csv_file', 'create_dict_from_csv'],
        'max-line-length': 120
    })
