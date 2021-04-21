from extractPropertiesFromNDJSON import extractProperties
from PropertyDist import property_count_function
from pathlib import Path
import pandas as pd
import numpy as np

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

mis_dataframe = property_count_function(property_list)
