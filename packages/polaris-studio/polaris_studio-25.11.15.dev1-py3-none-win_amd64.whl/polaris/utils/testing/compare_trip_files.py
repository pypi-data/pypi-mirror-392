# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from typing import Optional

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from polaris.analyze.demand_report import add_mode_names, vmts, time_distribution, trips_by_mode, trips_by_type


def demand_comparison(trips_base: pd.DataFrame, trips_new: pd.DataFrame, locations : Optional[gpd.GeoDataFrame] = None):
    if min(trips_new.shape[0], trips_base.shape[0]) == 0:
        logging.error("One of the Trips dataframes is empty")
        return

    locs = gpd.GeoDataFrame([]) if locations is None else locations
    trips_base = add_mode_names(trips_base)
    trips_new = add_mode_names(trips_new)

    rows = 6
    fig, axs = plt.subplots(rows, 2, figsize=(20, rows * 6), sharey=False)

    # Compares trips by mode
    _ = trips_by_mode(trips_base, cname="Base", ax=axs[0, 0], ax_table=axs[1, 0])
    _ = trips_by_mode(trips_new, cname="New", ax=axs[0, 1], ax_table=axs[1, 1])

    # Compares VMTs
    cond1 = any(col not in trips_base.columns for col in ["euclidean", "manhatan"])
    cond2 = any(col not in trips_new.columns for col in ["euclidean", "manhatan"])
    if locations is None and cond1 and cond2:
        logging.error("VMT report is not possible without locations")
    else:
        _ = vmts(trips_base, locs, axs[2, 0], name=" (Base)")
        _ = vmts(trips_new, locs, axs[2, 1], name=" (NEW)")

    # Compares trips by type
    _ = trips_by_type(trips_base, cname="Base", ax=axs[3, 0], ax_table=axs[4, 0])
    _ = trips_by_type(trips_new, cname="New", ax=axs[3, 1], ax_table=axs[4, 1])

    # Compare time distributions
    _ = time_distribution(trips_base, field_name="Base", ax=axs[5, 0])
    _ = time_distribution(trips_new, field_name="New", ax=axs[5, 0])

    return fig
