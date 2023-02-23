import shutil
from os.path import join

import yaml


def user_change_controls(overwrite=False, **kwargs):
    """
    Allows the user to input the control files if one wish to use other variables rather than those provided by Tradesman.

    Parameters:
         *overwrite*(:obj:`bool`): replaces the control file. Default: False
         *src_file*(:obj:`str`): path to the new control file
         *dest_folder*(:obj:`str`): path to folder where synthetic population is

    """
    if overwrite is True:
        shutil.move(kwargs["src_file"], join(kwargs["dest_folder"], "configs/controls.csv"))


def user_change_settings(overwrite=False, **kwargs):
    """
    Allows the user to set other variables for the synthetic population. By default, for synthetic persons information related to age, sex, occupation, journey to work and race are provided. As for synthetic households, the information provided are number of persons in the household and average household income.

    Parameters:
         *overwrite*(:obj:`bool`): replaces the settings file. Default: False
         *household_settings*(:obj:`list`): list with household parameters to add
         *persons_settings*(:obj:`list`): list with persons parameters to add
         *dest_folder*(:obj:`str`): path to folder where synthetic population is

    """
    if overwrite is True:
        with open(join(kwargs["dest_folder"], "configs/settings.yaml"), encoding="utf-8") as file:
            doc = yaml.full_load(file)

        doc["output_synthetic_population"]["households"]["columns"] += kwargs["household_settings"]
        doc["output_synthetic_population"]["persons"]["columns"] += kwargs["persons_settings"]

        with open(join(kwargs["dest_folder"], "configs/settings.yaml"), "w", encoding="utf-8") as file:
            yaml.safe_dump(doc, file, default_flow_style=False)


def user_import_new_seeds(overwrite=False, **kwargs):
    """
    Allows the user to set their own seed_persons and seed_household files. It is mandatory to provide the new control_totals for the existing geographical units.

    Parameters:
         *overwrite*(:obj:`bool`): replaces seed_households and seed_persons files. Default: False
         *persons_seed_path*(:obj:`str`): path to new seed_persons file
         *household_seed_path*(:obj:`str`): path to new seed_households file
         *dest_folder*(:obj:`str`): path to folder where synthetic population is

    """
    if overwrite is True:
        shutil.move(kwargs["persons_seed_path"], join(kwargs["dest_folder"], "data/seed_persons.csv"))
        shutil.move(kwargs["household_seed_path"], join(kwargs["dest_folder"], "data/seed_households.csv"))


def user_import_new_totals(overwrite=False, **kwargs):
    """
    Allows the user to change the existing controls. One must pay close attention to the geographical encoding of areas, once it must be the same for all files.

    Parameters:
         *overwrite*(:obj:`bool`): replaces the geo_cross_walk, control_totals_taz and control_totals_meta files. Default: False
         *totals_lower_level*(:obj:`str`): path to the new control_totals_taz file
         *totals_upper_level*(:obj:`str`): path to the new control_totals_meta file
         *geographies*(:obj:`str`): path to the new geo_cross_walk file
         *dest_folder*(:obj:`str`): path to folder where synthetic population is

    """
    if overwrite is True:
        shutil.move(kwargs["totals_lower_level"], join(kwargs["dest_folder"], "data/control_totals_taz.csv"))
        shutil.move(kwargs["totals_upper_level"], join(kwargs["dest_folder"], "data/control_totals_meta.csv"))
        shutil.move(kwargs["geographies"], join(kwargs["dest_folder"], "data/geo_cross_walk.csv"))


def user_change_geographies(overwrite=False, **kwargs):
    """
    Replaces values in settings.yaml file in case the geographies provided in the new files are different than TAZ < PUMA < REGION.

    Parameters:
         *overwrite*(:obj:`bool`): replaces the geography configurations in settings file. Default: False
         *seed_geography*(:obj:`str`):
         *upper_geography*(:obj:`str`):
         *lower_geography*(:obj:`str`):
         *dest_folder*(:obj:`str`): path to folder where synthetic population is
    """
    if overwrite is True:
        with open(join(kwargs["dest_folder"], "configs/settings.yaml"), encoding="utf-8") as file:
            doc = yaml.full_load(file)

        doc["seed_geography"] = kwargs["seed_geography"]
        doc["geographies"] = [kwargs["upper_geography"], kwargs["seed_geography"], kwargs["lower_geography"]]

        with open(join(kwargs["dest_folder"], "configs/settings.yaml"), "w", encoding="utf-8") as file:
            yaml.safe_dump(doc, file, default_flow_style=False)


def user_change_validation_parameters(overwrite: bool, model_place: str, dest_folder: str, **kwargs):
    """
    Replaces validation parameters in case of changes in geographies and/or controls.

    Parameters:
          *overwrite*(:obj:`bool`): replaces the validation file. Default: False
          *model_place*(:obj:`str`): current model place
          *dest_folder*(:obj:`str`): path to folder where synthetic population is
          *aggregate_summaries*: list of dictionaries containing the name, geography, control, and result. Will rewrite the default summary.
          *geographies*: list containing the existing geographies, from upper to lower levels (e.g: ['REGION', 'PUMA', 'TAZ'])
    """

    with open(join(dest_folder, "verification.yaml"), encoding="utf-8") as file:
        doc = yaml.full_load(file)

    doc["popsim_dir"] = "population"
    doc["region"] = model_place
    doc["validation_dir"] = "validation_results"

    if overwrite is True:
        doc["aggregate_summaries"] = kwargs["aggregate_summaries"]
        doc["group_geographies"] = kwargs["geographies"]

    with open(join(dest_folder, "verification.yaml"), "w", encoding="utf-8") as file:
        yaml.safe_dump(doc, file, default_flow_style=False)
