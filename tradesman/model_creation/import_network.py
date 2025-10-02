import csv
import gc
from pathlib import Path
from time import sleep

import pandas as pd
import requests
from aequilibrae import Parameters
from aequilibrae.project import Project
from aequilibrae.utils.db_utils import commit_and_close

from tradesman.model_creation.extra_data_fields import extra_fields
from tradesman.utils import set_bbox


class ImportNetwork:
    """
    Imports network from OSM or allows the user to manually import network from .osm or .pbf files.

    Parameters:
        *project*(:obj:`aequilibrae.project.Project`): currently open project

        *pbf_path*(:obj:`str`): path to osm or pbf file. Optional.

    """

    def __init__(self, project: Project, pbf_path: str = None, box_side: int = 25):
        self.project = project
        self.pbf_path = pbf_path
        self.box_side = box_side
        self.json = []

        self.db_path = self.project.project_base_path / "project_database.sqlite"

    def build_network(self):
        """
        Builds the network.
        """
        par = Parameters()
        try:
            requests.get("https://lz4.overpass-api.de/api/interpreter")
        except requests.exceptions.ConnectionError:
            par.parameters["osm"]["overpass_endpoint"] = "https://overpass.kumi.systems/api/interpreter"
            par.write_back()

        if not self.pbf_path:
            par.parameters["network"]["links"]["fields"]["one-way"].extend(extra_fields)
            par.write_back()

            self.project.network.create_from_osm(place_name=self.project.about.model_place)
            return

        else:
            import osm2gmns as og

            print("Convert to GMNS ...")
            print(" ")
            net = og.getNetFromFile(self.pbf_path)
            og.outputNetToCSV(net, output_folder=str(self.project.project_base_path))

            print("Adjust GMNS files ...")
            print(" ")
            self.__adjust_link_file(self.project.project_base_path / "link.csv")

            link_fields = {"osm_way_id": {"description": "osm_id", "type": "text", "required": False}}
            node_fields = {"osm_node_id": {"description": "osm_id", "type": "text", "required": False}}

            par.parameters["network"]["gmns"]["link"]["fields"].update(link_fields)
            par.parameters["network"]["gmns"]["node"]["fields"].update(node_fields)
            par.write_back()

            print("Create network from GMNS ...")
            print(" ")
            self.project.network.create_from_gmns(
                link_file_path=self.project.project_base_path / "link.csv",
                node_file_path=self.project.project_base_path / "node.csv",
            )

            print(" ")
            print("Download OSM data for bridges, tolls and tunnels ...")
            print(" ")
            self.__download_osm_data()

            print("Add new columns ...")
            print(" ")
            self.__setup_tables()

            print("Update links ...")
            print(" ")
            self.__update_links()

    def __adjust_link_file(self, file_path: Path):
        """
        Fix files created from osm2gmns to fit AequilibraE create_from_gmns.

        Parameters:
            *file_path*(:obj:`Path`):
        """
        df = pd.read_csv(file_path, sep=",", encoding="utf-8")

        all_values = df.allowed_uses.str.replace(";", ", ")
        rename_list = [element.replace("auto", "car").replace("bike", "bicycle") for element in all_values]
        df["allowed_uses"] = rename_list

        df.to_csv(file_path, sep=",", encoding="utf-8", index=False, quoting=csv.QUOTE_NONNUMERIC)

    def __download_osm_data(self):
        """Loads data from OSM"""
        url = self.project.parameters["osm"]["overpass_endpoint"]

        # We won't download any area bigger than 25km by 25km
        xmin = float(self.project.about.xmin)
        xmax = float(self.project.about.xmax)
        ymin = float(self.project.about.ymin)
        ymax = float(self.project.about.ymax)
        bboxes = set_bbox(xmin, ymin, xmax, ymax, self.box_side)

        http_headers = requests.utils.default_headers()
        http_headers.update({"Accept-Language": "en", "format": "json"})

        for tag in ["bridge", "toll", "tunnel"]:
            query = (
                f'[out:json][timeout:180];(way["highway"]["area"!~"yes"]["highway"!~"proposed|raceway|construction|abandoned|platform"]["service"!~"parking|parking_aisle|driveway|private|emergency_access"]["access"!~"private"]["{tag}"="yes"]'
                + "({});>;);out geom;"
            )
            for bbox in bboxes:
                bbox_str = ",".join([str(round(x, 6)) for x in bbox])
                data = {"data": query.format(bbox_str)}
                response = requests.post(url, data=data, timeout=180, headers=http_headers)
                if response.status_code != 200:
                    # raise ConnectionError("Could not download data")
                    sleep(2)
                    continue

                # get the response size and the domain, log result
                json = response.json()
                if json["elements"]:
                    self.json.extend(json["elements"])
                del json
                gc.collect()

    def __setup_tables(self):
        """
        Creates the missing columns when importing data from GMNS.
        """
        with commit_and_close(self.db_path, spatial=True) as conn:
            conn.execute("ALTER TABLE links ADD COLUMN bridge text;")
            conn.execute("ALTER TABLE links ADD COLUMN toll text;")
            conn.execute("ALTER TABLE links ADD COLUMN tunnel text;")

    def __update_links(self):
        """
        Updates the links which are bridge, toll or tunnel.
        """
        bridge_list = []
        toll_list = []
        tunnel_list = []

        for element in self.json:
            if element["type"] == "way":
                for tag in element["tags"]:
                    if tag == "bridge":
                        bridge_list.append(element["id"])
                    elif tag == "toll":
                        toll_list.append(element["id"])
                    elif tag == "tunnel":
                        tunnel_list.append(element["id"])

        bridge_list = [(x,) for x in bridge_list]
        toll_list = [(x,) for x in toll_list]
        tunnel_list = [(x,) for x in tunnel_list]

        with commit_and_close(self.db_path, spatial=True) as conn:
            conn.executemany("UPDATE links SET bridge='yes' WHERE osm_way_id=?;", bridge_list)
            conn.executemany("UPDATE links SET toll='yes' WHERE osm_way_id=?;", toll_list)
            conn.executemany("UPDATE links SET tunnel='yes' WHERE osm_way_id=?;", tunnel_list)
