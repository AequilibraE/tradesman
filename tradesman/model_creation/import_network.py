import gc
import csv
from tempfile import gettempdir
from time import sleep
from aequilibrae import Project, Parameters
from os.path import join

import pandas as pd
import requests

from tradesman.model_creation.extra_data_fields import extra_fields
from tradesman.data_retrieval.osm_tags.set_bounding_boxes import bounding_boxes


class ImportNetwork:
    """
    Imports network from OSM or allows the user to manually import network from .osm or .pbf files.

    Parameters:
        *project*(:obj:`aequilibrae.project.Project`): currently open project
        *model_place*(:obj:`str`): current model place
        *pbf_path*(:obj:`str`): path to osm or pbf file. Optional.

    """

    def __init__(self, project: Project, model_place: str, pbf_path: str = None):
        self.project = project
        self.model_place = model_place
        self.pbf_path = pbf_path
        self.json = []
        self.par = Parameters()
        self.new_link_fields = {
            "osm_way_id": {"description": "osm_id", "type": "text", "required": False},
        }
        self.new_node_fields = {"osm_node_id": {"description": "osm_id", "type": "text", "required": False}}

    def build_network(self):
        """
        Builds the network.
        """
        try:
            requests.get("https://lz4.overpass-api.de/api/interpreter")
        except requests.exceptions.ConnectionError:
            self.par.parameters["osm"]["overpass_endpoint"] = "https://overpass.kumi.systems/api/interpreter"
            self.par.write_back()

        if not self.pbf_path:
            self.par.parameters["network"]["links"]["fields"]["one-way"].extend(extra_fields)
            self.par.write_back()
            self.project.network.create_from_osm(place_name=self.model_place)
            return

        else:
            import osm2gmns as og

            print("Convert to GMNS ...")
            print(" ")
            net = og.getNetFromFile(self.pbf_path, network_types=("auto"))
            og.outputNetToCSV(net, output_folder=gettempdir(), prefix=f"{self.model_place}-gmns-", encoding="utf-8")

            print(" ")
            print("Adjust GMNS files ...")
            print(" ")
            self.__adjust_link_file(
                file_path=join(gettempdir(), f"{self.model_place}-gmns-link.csv"), model_place=self.model_place
            )

            self.par.parameters["network"]["gmns"]["link"]["fields"].update(self.new_link_fields)
            self.par.parameters["network"]["gmns"]["node"]["fields"].update(self.new_node_fields)
            self.par.write_back()

            print("Create network from GMNS ...")
            print(" ")
            self.project.network.create_from_gmns(
                link_file_path=join(gettempdir(), f"{self.model_place}-gmns-link.csv"),
                node_file_path=join(gettempdir(), f"{self.model_place}-gmns-node.csv"),
            )

            print(" ")
            print("Download OSM data for bridges, tolls and tunnels ...")
            print(" ")
            self.__download_osm_data(model_place=self.model_place)

            print("Add new columns ...")
            print(" ")
            self.__setup_tables()

            print("Update links ...")
            print(" ")
            self.__update_links()

    def __adjust_link_file(self, file_path: str, model_place: str):
        """
        Fix files created from osm2gmns to fit AequilibraE create_from_gmns.

        Parameters:
             *file_path*(:obj:`str`):
             *model_place*(:obj:`str`):
        """
        df = pd.read_csv(file_path, sep=",", encoding="utf-8")
        # Rename directions
        directions_dict = {1: "forward", -1: "backward", 0: "bidirectional"}
        df["dir_flag"] = df["dir_flag"].apply(lambda x: directions_dict.get(x))
        # Drop link_type column
        df.drop(columns=["link_type"], inplace=True)
        # Rename link_type_name column to link_type
        df.rename(columns={"link_type_name": "link_type", "dir_flag": "directed"}, inplace=True)

        all_values = df.allowed_uses.str.replace(";", ", ")

        rename_list = []
        for element in all_values:
            element = element.replace("auto", "car").replace("bike", "bicycle")
            rename_list.append(element)

        df["allowed_uses"] = rename_list

        df.to_csv(
            join(gettempdir(), f"{model_place}-gmns-link.csv"),
            sep=",",
            encoding="utf-8",
            index=False,
            quoting=csv.QUOTE_NONNUMERIC,
        )

    def __download_osm_data(self, model_place: str, tile_size: int = 25):
        """
        Loads data from OSM.

        Parameters:
             *model_place*(:obj:`str`):
             *tile_size*(:obj:`int`):
        """
        url = self.project.parameters["osm"]["overpass_endpoint"]

        # We won't download any area bigger than 25km by 25km
        bboxes = bounding_boxes(self.project, tile_size)

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
        self.project.conn.execute("ALTER TABLE links RENAME COLUMN osm_way_id TO osm_id;")

        self.project.conn.execute("ALTER TABLE links ADD COLUMN bridge text;")
        self.project.conn.execute("ALTER TABLE links ADD COLUMN toll text;")
        self.project.conn.execute("ALTER TABLE links ADD COLUMN tunnel text;")

        self.project.conn.commit()

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

        self.project.conn.executemany("UPDATE links SET bridge='yes' WHERE osm_id=?;", bridge_list)
        self.project.conn.executemany("UPDATE links SET toll='yes' WHERE osm_id=?;", toll_list)
        self.project.conn.executemany("UPDATE links SET tunnel='yes' WHERE osm_id=?;", tunnel_list)
        self.project.conn.commit()
