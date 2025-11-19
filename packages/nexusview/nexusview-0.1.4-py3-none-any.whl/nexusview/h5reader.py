"""
Main class to read a nexus file and export its output
"""
import os
import logging
from collections import namedtuple  # type: ignore

import h5py  # HDF5 support
import pandas as pd  # type: ignore
from termcolor import colored  # type: ignore

logging.basicConfig(level=logging.INFO)

class H5reader(object):
    """Class allowing to read and parse NeXus/hdf5 files"""

    def __init__(self, h5_filename):

        self.h5_basename = os.path.basename(h5_filename).split(".")[0]
        print(self.h5_basename)
        try:
            self.h5_handle = h5py.File(h5_filename, "r")

        except OSError as error:
            print("Problem with opening the file", h5_filename)
            print(error)
            self.h5_handle = None

        # List of namedtuples, each of which contains a metadata record
        self.metadata_list = []

        # metadata can be NeXus attributes or datasets
        self.Metarecord = namedtuple(  # pylint: disable=C0103
            "Metarecord",
            ["name", "type", "value", "parent_group", "parent_dataset"],
        )
        # if more than this numbe rof elements in a dataset
        # don't display it
        self.NELEM_DISPLAY = 10  # pylint: disable=C0103

    def read(self):
        """Calls the recursive_read function"""
        # Read in a recursive way
        self._recursive_read(self.h5_handle)

        # Don't forget to close your file handle afterwards
        if self.h5_handle is not None:
            self.h5_handle.close()

    @staticmethod
    def display_attributes(list_of_tups, spaces):
        """
        display the list of attributes entered as a list of tuples
        (key, value) list_of_tups

        :param:spaces: str, a sting made of several repetitions of "--"
        """
        for key, value in list_of_tups:
            # print(tup)
            #                        for key, value in tup:
            print(spaces + "--", colored("@" + key, "green"), ":", value)

    def record_attributes(self, list_of_tups, parent_group, parent_dataset):
        """Records the attributes as metadata
        entered as namedtuples in self.metadata_list

        """
        for key, value in list_of_tups:
            self.metadata_list.append(
                self.Metarecord(
                    "@" + key, "attribute", value, parent_group, parent_dataset
                )
            )

    def describe_dataset(self, dataset_obj):
        """
        Format a description of a NeXus dataset depending on its size and shape
        """
        if dataset_obj.shape:  # if the dimensions is not an empty tuple
            if (
                dataset_obj.ndim > 1
            ):  # more than 1 dimension, only display shape
                ds_description = "shape: " + str(dataset_obj.shape)

            elif dataset_obj.shape[0] > self.NELEM_DISPLAY:
                # 1 dimension and many elements--> display only nelem
                ds_description = "shape: " + str(dataset_obj.shape)

            elif dataset_obj.shape[0] <= self.NELEM_DISPLAY:
                # 1 dimension and few elements: display them
                ds_description = " ".join([str(x) for x in dataset_obj[:]])

        # scalar datasets
        elif isinstance(dataset_obj[()], bytes):
            ds_description = dataset_obj[()].decode()
        else:
            ds_description = str(dataset_obj[()])

        return ds_description

    def record_dataset(self, dataset_name, dataset_obj):
        """
        Adds a dataset to the list of metadata records
        The value will be its dimensionality for now
        """

        ds_description = self.describe_dataset(dataset_obj)
        self.metadata_list.append(
            self.Metarecord(
                dataset_name,
                "dataset",
                ds_description,
                dataset_obj.parent.name,
                "na",
            )
        )

    def _recursive_read(self, obj, level: int = 0):
        """
        Reads and hdf5 in a recursive way
        :param:obj: a hdf5 object return by h5py.File read as a list of
        tuples (key=name, val=group/dataset)

        It also gathers metadata as namedtuples in the self.metadata_list
        """
        # spaces to add in front of group or dataset names
        spaces = "--" * level

        if obj is not None:

            for field_name, field_ref in obj.items():

                try:
                    attributes = [(a, b) for a, b in field_ref.attrs.items()]
                except AttributeError:
                    attributes = []

                plural = "s" if len(attributes) > 1 else ""

                if isinstance(field_ref, h5py.Group):
                    print(
                        spaces,
                        colored(field_name, "blue"),
                        "-->",
                        len(attributes),
                        "attribute" + plural,
                    )

                    H5reader.display_attributes(attributes, spaces)
                    self.record_attributes(
                        attributes, field_ref.parent.name, field_name + "_G"
                    )
                    self._recursive_read(field_ref, level + 1)

                elif isinstance(field_ref, h5py.Dataset):

                    print(spaces, colored(field_name, "red"), "--> ", end="")
                    print(self.describe_dataset(field_ref))

                    H5reader.display_attributes(attributes, spaces)
                    self.record_attributes(
                        attributes, field_ref.parent.name, field_name + "_DS"
                    )
                    self.record_dataset(field_name + "_DS", field_ref)

                elif field_ref is None:
                    print(spaces, colored(field_name, "red"), "--> No description")



        else:
            print("nothing to read")

    def create_csv(self):
        """
        Creates an Excel file out of the metadata records list
        """

        dataframe = pd.DataFrame(data=self.metadata_list)

        # here we want the name column to be as follows
        # if dataset: dataset name
        # if attribute: dataset@attribute
        # We create a new column to handle that
        dataframe["isattr"] = dataframe["name"].apply(
            lambda s: 1 if s.startswith("@") else 0
        )

        dataframe["dataset/attribute"] = dataframe["name"].where(
            (dataframe["isattr"] == 0)
            | (
                (dataframe["isattr"] == 1)
                & (dataframe["parent_dataset"] == "na")
            ),
            dataframe["parent_dataset"] + dataframe["name"],
        )

        # Exporting
        cols = ["parent_group", "dataset/attribute", "value"]
        print("Exporting Metadata to csv file")
        file_out = self.h5_basename + ".csv"
        dataframe[cols].sort_values(
            by=["parent_group", "dataset/attribute"]
        ).to_csv(file_out)
        print("Done:", file_out)
