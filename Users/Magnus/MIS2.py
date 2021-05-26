from Finished_Code.extractPropertiesFromNDJSON import extractProperties
from Finished_Code.findPropertyDist import property_count_function
from pathlib import Path

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

mis_dataframe = property_count_function(property_list)

param = 0.95

mis_dataframe.set_index(['Property'], inplace=True)
mis_dataframe['MIS'] = [param * mis_dataframe['Frequency'][i]/mis_dataframe['Frequency']['P31'] for i in range(len(mis_dataframe))]


def convertMISListToTXT(MISList, output_filename, sdc):
    with open(output_filename, 'w') as f:
        for i in MISList.index:
            try:
                f.write('MIS(' + str(i[1:]) + ') = ' + str("{:.9f}".format((MISList[i]))))
                f.write("\n")
            except TypeError:
                print('The type of data is wrong')
        f.write('SDC = ' + str(sdc))
        f.close()

convertMISListToTXT(mis_dataframe['MIS'], 'mis.txt', 0.9)