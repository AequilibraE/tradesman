from math import floor
from os.path import join, dirname

import numpy as np
import pandas as pd
import tabulate
from aequilibrae.project import Project


def create_buckets(project: Project, folder: str, sample=0.02):
    """
    Creates buckets containing households and population info.
    This function outputs are the inputs for creating the seeds.

    Parameters:
         *project*(:obj:`aequilibrae.Project`): current project
         *folder*(:obj:`str`): folder containing PopulationSim population files
         *sample*(:obj:`float`): percentage of population one want to compose the seed.
    """

    country_code = project.about.country_code

    pth = dirname(__file__)

    household_info = pd.read_csv(join(pth, "controls_and_validation/hh_size_data.csv"))

    household_info = household_info[household_info.iso_code == country_code]

    household_info.reset_index(drop=True, inplace=True)

    population = int(project.conn.execute("SELECT ROUND(SUM(population),0) FROM zones;").fetchone()[0])

    # Set the sample proportion
    sort_number = int((population * sample) / household_info.AVGSIZE[0])

    seed_households = pd.read_csv(join(folder, "data/seed_households.csv"))

    seed_persons = pd.read_csv(join(folder, "data/seed_persons.csv"))

    sorted_numbers = np.random.random(size=sort_number)  # random numbers

    tops_1 = (household_info.HHBASE1 / 100).tolist()[0]

    tops_2 = tops_1 + (household_info.HHBASE2 / 100).tolist()[0]

    tops_4 = tops_2 + (household_info.HHBASE4 / 100).tolist()[0]

    prop_1 = []  # number of households with 1 person
    prop_2 = []  # number of households with 2-3 person
    prop_4 = []  # number of households with 4-5 person
    prop_6 = []  # number of households with 6+ person

    for i in sorted_numbers:
        if i <= tops_1:
            prop_1.append(i)
        elif tops_1 < i <= tops_2:
            prop_2.append(i)
        elif tops_2 < i <= tops_4:
            prop_4.append(i)
        else:
            prop_6.append(i)

    num_hh = [prop_1, prop_2, prop_4, prop_6]

    # Return infos about the number of seeds to be sorted
    __show_seed_stats(num_hh=num_hh, sort_number=sort_number, household_info=household_info)

    # Create the buckets containing households (by size) and persons (according to the household size they live in)
    house_bucket_1 = seed_households[seed_households.NP == 1]

    house_bucket_2 = seed_households[(seed_households.NP == 2) | (seed_households.NP == 3)]

    house_bucket_4 = seed_households[(seed_households.NP == 4) | (seed_households.NP == 5)]

    house_bucket_6 = seed_households[seed_households.NP >= 6]

    persons_bucket_1 = seed_persons[seed_persons.hhnum.isin(house_bucket_1.hhnum.tolist())]

    persons_bucket_2 = seed_persons[seed_persons.hhnum.isin(house_bucket_2.hhnum.tolist())]

    persons_bucket_4 = seed_persons[seed_persons.hhnum.isin(house_bucket_4.hhnum.tolist())]

    persons_bucket_6 = seed_persons[seed_persons.hhnum.isin(house_bucket_6.hhnum.tolist())]

    households = [house_bucket_1, house_bucket_2, house_bucket_4, house_bucket_6]
    persons = [persons_bucket_1, persons_bucket_2, persons_bucket_4, persons_bucket_6]

    total_households = []
    total_persons = []

    int_part = [
        floor((len(num_hh[i]) / len(households[i]))) for i in range(4)
    ]  # range is 4 due to the number of buckets we have pre-set
    float_part = [(len(num_hh[i]) - (len(households[i]) * int_part[i])) for i in range(4)]

    for i in range(4):
        partial = households[i].sample(float_part[i])
        total_households.append(partial)
        total_persons.append(persons[i][persons[i].hhnum.isin(partial.hhnum.tolist())])
        for j in range(floor(int_part[i])):
            total_households.append(households[i])
            total_persons.append(persons[i])

    pd.concat(total_households).to_csv(join(folder, "data/seed_households.csv"), sep=",", index=False)

    pd.concat(total_persons).to_csv(join(folder, "data/seed_persons.csv"), sep=",", index=False)


def __show_seed_stats(num_hh, sort_number, household_info):
    """
    Prints the calculated and expected seed stats for the population sample.

    Parameters:
         *num_hh*(:obj:`list`): list with the number of households per bucket
         *sort_number*(:obj:`int`): number of households to sample
         *household_info*(:obj:`pandas.DataFrame`): pandas.DataFrame with household proportion information
    """
    print("Calculated vs Expected percentage of households per size in the sample")
    print("")
    table_1 = [
        ["1 person", round((len(num_hh[0]) / sort_number) * 100, 2), household_info.HHBASE1.tolist()[0]],
        ["2-3 person", round((len(num_hh[1]) / sort_number) * 100, 2), household_info.HHBASE2.tolist()[0]],
        ["4-5 person", round((len(num_hh[2]) / sort_number) * 100, 2), household_info.HHBASE4.tolist()[0]],
        ["6+ person", round((len(num_hh[3]) / sort_number) * 100, 2), household_info.HHBASE6.tolist()[0]],
    ]

    print(tabulate.tabulate(table_1, headers=["# Person", "Calculated", "Expected"]))
    print("")

    print("Difference in calculated vs expected percentage of households in the sample")
    print("")
    table_2 = [
        ["1 person", round((len(num_hh[0]) / sort_number) * 100 - household_info.HHBASE1.tolist()[0], 2)],
        ["2-3 person", round((len(num_hh[1]) / sort_number) * 100 - household_info.HHBASE2.tolist()[0], 2)],
        ["4-5 person", round((len(num_hh[2]) / sort_number) * 100 - household_info.HHBASE4.tolist()[0], 2)],
        ["6+ person", round((len(num_hh[3]) / sort_number) * 100 - household_info.HHBASE6.tolist()[0], 2)],
    ]

    print(tabulate.tabulate(table_2, headers=["# Person", "Diff."]))
    print("")
