import pandas as pd
from aequilibrae.project import Project


def create_control_totals_taz(project: Project):

    zoning = project.zoning
    fields = zoning.fields

    selected_fields = []

    for field in fields:
        if 'f_pop_' or 'm_pop' in field:
            selected_fields.append(field)

    selection_qry = ""

    
    pass