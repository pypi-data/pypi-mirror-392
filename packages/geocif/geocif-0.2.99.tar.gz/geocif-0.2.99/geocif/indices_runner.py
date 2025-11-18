import itertools
import warnings
import ast
from multiprocessing import Pool, cpu_count
from pathlib import Path

import arrow as ar
import pandas as pd
from tqdm import tqdm

warnings.filterwarnings("ignore")

from .cei import indices
from geoprepare import base


def remove_duplicates(lst):
    """

    :param lst:
    :return:
    """
    return list(set([i for i in lst]))


def get_admin_zone(country, parser):
    """
    Get admin zone and admin column name from config file for the given country.
    Falls back to DEFAULT section if not specified for country.
    
    :param country: Country name
    :param parser: ConfigParser object
    :return: tuple of (admin_zone, admin_col_name)
    """
    country = country.title().replace(" ", "_")
    country_lower = country.lower()
    
    # Try to get admin_zone from country-specific section
    if parser.has_section(country_lower) and parser.has_option(country_lower, "admin_zone"):
        admin_zone = parser.get(country_lower, "admin_zone")
    # Fall back to DEFAULT section
    elif parser.has_option("DEFAULT", "admin_zone"):
        admin_zone = parser.get("DEFAULT", "admin_zone")
    else:
        raise ValueError(f"admin_zone not specified for country {country} in config file.")
    
    # Try to get admin_col_name from country-specific section
    if parser.has_section(country_lower) and parser.has_option(country_lower, "admin_col_name"):
        admin_col_name = parser.get(country_lower, "admin_col_name")
    # Fall back to DEFAULT section
    elif parser.has_option("DEFAULT", "admin_col_name"):
        admin_col_name = parser.get("DEFAULT", "admin_col_name")
    # Final fallback
    else:
        raise ValueError(f"admin_col_name not specified for country {country} in config file.")
    
    return admin_zone, admin_col_name


def get_input_file_path(country, parser):
    """
    Get input file path from config file for the given country.
    Falls back to DEFAULT section if not specified for country.
    Uses variable substitution from PATHS section (e.g., ${dir_crop_inputs}/processed)
    
    :param country: Country name
    :param parser: ConfigParser object
    :return: Path object for input files
    """
    country_lower = country.lower().replace(" ", "_")
    
    # Try to get input_file_path from country-specific section
    if parser.has_section(country_lower) and parser.has_option(country_lower, "input_file_path"):
        path_str = parser.get(country_lower, "input_file_path")
    # Fall back to DEFAULT section
    elif parser.has_option("DEFAULT", "input_file_path"):
        path_str = parser.get("DEFAULT", "input_file_path")
    else:
        raise ValueError(f"input_file_path not specified for country {country} in config file.")
    
    # ConfigParser with ExtendedInterpolation should handle ${var} substitution automatically
    # Convert forward slashes to backslashes on Windows for consistency
    return Path(path_str)


class cei_runner(base.BaseGeo):
    def __init__(self, path_config_file):
        super().__init__(path_config_file)

        # Parse configuration files
        self.parse_config()

        # Get base input path from DEFAULT section
        # Variable substitution (e.g., ${dir_crop_inputs}/processed) is handled by ConfigParser
        if self.parser.has_option("DEFAULT", "input_file_path"):
            self.base_dir = Path(self.parser.get("DEFAULT", "input_file_path"))
        else:
            raise ValueError("input_file_path not specified in DEFAULT section of config file.")
        
        self.do_parallel = self.parser.getboolean("DEFAULT", "do_parallel")
        
        # Read countries and methods from config file
        self.countries = ast.literal_eval(self.parser.get("DEFAULT", "countries"))
        self.method = self.parser.get("DEFAULT", "method")

    def collect_files(self):
        """
        1. Collect all the files which contain EO information
        2. Exclude files from the `processed` directory if it is already in
        processed_include_fall directory
        3. Create a dataframe that contains the following columns:
            - directory: name of directory where file is located
            - path: full path to file
            - filename: name of file
            - admin_zone: admin zone level
            - admin_col_name: column name for admin boundaries
        :return: Return the dataframe created above
        """
        # Collect all the files which contain EO information
        df_files = pd.DataFrame(columns=["directory", "path", "filename", "admin_zone", "admin_col_name"])
        
        # If specific countries are defined, check their paths individually
        if self.countries and self.countries != ['all']:
            for country in self.countries:
                country_path = get_input_file_path(country, self.parser)
                
                for filepath in country_path.rglob("*.csv"):
                    country_name = filepath.parents[0].name

                    # Get admin_zone and admin_col_name from config file
                    admin_zone, admin_col_name = get_admin_zone(country_name, self.parser)

                    # HACK: Skip korea for now, as it is giving errors
                    if country_name == "republic_of_korea":
                        continue

                    # Get name of directory one level up
                    process_type = filepath.parents[1].name

                    # Get name of file
                    filename = filepath.name

                    # Add to dataframe
                    df_files.loc[len(df_files)] = [process_type, filepath, filename, admin_zone, admin_col_name]
        else:
            # Use base directory for all countries
            for filepath in self.base_dir.rglob("*.csv"):
                country = filepath.parents[0].name

                # Get admin_zone and admin_col_name from config file
                admin_zone, admin_col_name = get_admin_zone(country, self.parser)

                # HACK: Skip korea for now, as it is giving errors
                if country == "republic_of_korea":
                    continue

                # Get name of directory one level up
                process_type = filepath.parents[1].name

                # Get name of file
                filename = filepath.name

                # Add to dataframe
                df_files.loc[len(df_files)] = [process_type, filepath, filename, admin_zone, admin_col_name]

        # Exclude those rows where directory is processed and file is already in
        # processed_include_fall directory
        no_fall = df_files["directory"] == "processed"
        include_fall = df_files[df_files["directory"] == "processed_include_fall"][
            "filename"
        ]

        df_files = df_files[~(no_fall & (df_files["filename"].isin(include_fall)))]

        return df_files

    def process_combinations(self, df, method):
        """
        Create a list of tuples of the following:
            - directory: name of directory where file is located
            - path: full path to file
            - filename: name of file
            - method: whether to compute indices for phenological stages or not
        This tuple will be used as input to the `process` function
        :param df:
        :param method:
        :return:
        """
        combinations = []

        for index, row in tqdm(df.iterrows()):
            combinations.extend(
                list(
                    itertools.product([row[0]], [row[1]], [row[2]], [row[3]], [method])
                )
            )

        combinations = remove_duplicates(combinations)

        return combinations

    def main(self):
        """

        :param method:
        :return:
        """
        # Create a dataframe of the files to be analyzed
        df_files = self.collect_files()

        combinations = self.process_combinations(df_files, self.method)

        # Add an element to the tuple to indicate the season
        # Last element is redo flag which is True if the analysis is to be redone
        # and False otherwise. Analysis is always redone for the current year
        # and last year whether file exists or not
        combinations = [
            (
                self.parser,
                status,
                path,
                filename,
                admin_zone,
                category,
                year,
                "ndvi",
                False,  # redo
            )
            for year in range(2001, ar.utcnow().year + 1)
            for status, path, filename, admin_zone, category in combinations
        ]

        # Filter combinations based on countries from config file
        if self.countries and self.countries != ['all']:
            combinations = [
                i
                for i in combinations
                if any(country.lower().replace(" ", "_") in i[3].lower() 
                       for country in self.countries)
            ]

        if self.do_parallel:
            num_cpu = int(cpu_count() * 0.75)
            with Pool(num_cpu) as p:
                for i, _ in enumerate(p.imap_unordered(indices.process, combinations)):
                    pass
        else:
            # Use the code below if you want to test without parallelization or
            # if you want to debug by using pdb
            pbar = tqdm(combinations)
            for i, val in enumerate(pbar):
                pbar.set_description(
                    f"Main loop {combinations[i][2]} {combinations[i][5]}"
                )
                indices.process(val)


def run(path_config_files=[]):
    """

    Args:
        path_config_files:

    Returns:

    """
    """ Check dictionary keys to have no spaces"""
    indices.validate_index_definitions()

    obj = cei_runner(path_config_files)
    
    # Iterate over methods from config file
    obj.main()


if __name__ == "__main__":
    run()