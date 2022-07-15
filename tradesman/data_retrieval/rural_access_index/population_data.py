from tradesman.data_retrieval.rural_access_index.urban_areas import select_urban_areas

from tradesman.data_retrieval.load_vectorized_pop import load_vectorized_pop


def population_data(project):

    population = load_vectorized_pop(project)

    urban_areas = select_urban_areas(project)

    return population.overlay(urban_areas, how="difference")
