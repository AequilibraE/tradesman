from os.path import join
import shutil
import yaml


def user_control_import(overwrite: bool, folder: str, **kwargs):
    """
    Allows the user to input the control files if one wish to use other variables rather than those provived by Tradesman.
    Args:
         *overwrite*
         *folder*
    Kwargs:
         *new_path*


    """
    if overwrite is True:
        shutil.move(kwargs["new_path"], join(folder, "configs/control.csv"))


def user_change_settings(overwrite: bool, folder: str, **kwargs):
    """
    Allows the user to set other variables for the synthetic population. By default, for synthetic persons information related to age, sex, occupation, journey to work and race are provided. As for synthetic households, the information provided are number of persons in the household and average household income.
    Args:
         *overwrite*
         *folder*
    Kwargs:
         *household_settings*
         *persons_settings*

    """
    if overwrite is True:
        with open(join(folder, "configs/settings.yaml"), encoding='utf-8') as file:
            doc = yaml.full_load(file)

        doc["output_synthetic_population"]["households"]["columns"].append(kwargs["household_settings"])
        doc["output_synthetic_population"]["persons"]["columns"].append(kwargs["persons_settings"])

        with open(join(folder, "configs/settings.yaml"), "w", encoding='utf-8') as file:
            yaml.safe_dump(doc, file, default_flow_style=False)


def user_import_new_seeds(overwrite: bool, folder: str, **kwargs):
    """
    Allows the user to set their own seed_persons and seed_household files. It is mandatory to provide the new control_totals for the existing geographical units.
    Args:
         *overwrite*
         *folder*
    Kwargs:
         *persons_seed_path*
         *household_seed_path*

    """
    if overwrite is True:
        shutil.move(kwargs["persons_seed_path"], join(folder, "data/seed_persons.csv"))
        shutil.move(kwargs["household_seed_path"], join(folder, "data/seed_households.csv"))


def user_import_new_totals(overwrite: bool, folder: str, **kwargs):
    """
    Allows the user to change the existing controls. One must pay close attention to the geographical encoding of areas, once it must be the same for all files.

    Args:
         *overwrite*
         *folder*
    Kwargs:
         *totals_lower_level*
         *totals_upper_level*
         *geographies*

    """
    if overwrite is True:
        shutil.move(kwargs["totals_lower_level"], join(folder, "data/control_totals_taz.csv"))
        shutil.move(kwargs["totals_upper_level"], join(folder, "data/control_totals_meta.csv"))
        shutil.move(kwargs["geographies"], join(folder, "data/geo_cross_walk.csv"))


def user_change_geographies(overwrite: bool, folder: str, **kwargs):
    """
    This function replaces values in settings.yaml file in case the geographies provided in the new files are different than TAZ < PUMA < REGION.
    Args:
         *overwrite*
         *folder*
    Kwargs:
         *seed_geography*
         *upper_geography*
         *lower_geography*
    """
    if overwrite is True:
        with open(join(folder, "configs/settings.yaml"), encoding='utf-8') as file:
            doc = yaml.full_load(file)

        doc["seed_geography"] = kwargs["seed_geography"]
        doc["geographies"] = [kwargs["upper_geography"], kwargs["seed_geography"], kwargs["lower_geography"]]

        with open(join(folder, "configs/settings.yaml"), "w", encoding='utf-8') as file:
            yaml.safe_dump(doc, file, default_flow_style=False)


def user_change_validation_parameters(overwrite: bool, model_place: str, folder: str, **kwargs):
    """
    This function identifies the model's locaation, and allows the replacement of validation parameters in case of changes in geopgraphies and/or controls.
    Args:
          *overwrite*:
          *model_place*:
          *folder*: path to folder where synthetic population is
    **kwargs:
          *aggregate_summaries*: list of dictionaries containing the name, geography, control, and result.
          *geographies*: list containing the existing geographies, from upper to lower levels (e.g: ['REGION', 'PUMA', 'TAZ'])
    """

    with open(join(folder, "verification.yaml"), encoding='utf-8') as file:
        doc = yaml.full_load(file)

    doc["popsim_dir"] = model_place
    doc["region"] = model_place

    if overwrite is True:
        doc["aggregate_summaries"] = kwargs["aggregate_summaries"]
        doc['group_geographies'] = kwargs['geographies']

    with open(join(folder, "verification.yaml"), "w", encoding='utf-8') as file:
        yaml.safe_dump(doc, file, default_flow_style=False)
