import pandas as pd
import numpy as np


def pop_data(country_df):

    country_age = sorted([int(i) for i in np.unique(country_df.Age)])

    description_field = []

    for i in range(len(country_age) - 1):
        description_field.append(
            "Women population " + str(country_age[i]) + " to " + str(country_age[i + 1]) + " years old."
        )
        description_field.append(
            "Men population " + str(country_age[i]) + " to " + str(country_age[i + 1]) + " years old."
        )

    description_field.append("Women population over " + str(country_age[-1]) + " years old.")
    description_field.append("Men population over " + str(country_age[-1]) + " years old.")

    columns_name = ["women_" + row.Age if row.Sex == "f" else "men_" + row.Age for _, row in country_df.iterrows()]

    return description_field, columns_name
