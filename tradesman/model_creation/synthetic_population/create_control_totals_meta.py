import pandas as pd
import csv
from os.path import join
from aequilibrae.project import Project


def create_control_totals_meta(project: Project):

    # TODO: fix temporary folder location

    folder = r""  # location of temporary folder

    df = pd.read_csv(join(folder, "control_totals_taz.csv"))

    hh_list = df[["HHBASE", "HHBASE1", "HHBASE2", "HHBASE4", "HHBASE6"]].sum().tolist()

    total_pop = (
        df.sum()[
            [
                "POPF1",
                "POPF2",
                "POPF3",
                "POPF4",
                "POPF5",
                "POPF6",
                "POPF7",
                "POPF8",
                "POPF9",
                "POPF10",
                "POPF11",
                "POPF12",
                "POPF13",
                "POPF14",
                "POPF15",
                "POPF16",
                "POPF17",
                "POPF18",
                "POPM1",
                "POPM2",
                "POPM3",
                "POPM4",
                "POPM5",
                "POPM6",
                "POPM7",
                "POPM8",
                "POPM9",
                "POPM10",
                "POPM11",
                "POPM12",
                "POPM13",
                "POPM14",
                "POPM15",
                "POPM16",
                "POPM17",
                "POPM18",
            ]
        ]
        .sum()
        .tolist()
    )

    hh_list.insert(0, 1)
    hh_list.insert(1, 1)
    hh_list.insert(2, total_pop)

    with open(join(folder, "control_totals_meta.csv"), "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(["PUMA", "REGION", "POPBASE", "HHBASE", "HHSIZE1", "HHSIZE2", "HHSIZE4", "HHSIZE6"])
        writer.writerow(hh_list)
