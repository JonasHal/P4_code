from extractPropertiesFromNDJSON import extractProperties
from PropertyDistUni import property_count_function
from pathlib import Path
import pandas as pd

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

mis_dataframe = property_count_function(property_list)
