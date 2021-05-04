import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, isnull, when, col
from pyspark.mllib.stat import Statistics
from pyspark.ml.feature import Imputer
import seaborn as sns

# # Check that you have all the import packages installed before beginning the exercises.
# # All the code have been outcommented once. The real comments have been outcommened twice. When doing the exercises
# # just outcomment the code line by line as you follow the exercises on the slides.

# # Exercise 1

# spark = SparkSession.builder.appName('name').getOrCreate()

# df = spark.read.options(header="True", inferSchema=True, delimiter=",") \
#     .csv("C:/Users/magnu/Downloads/pima-indians-diabetes.csv")

# df.printSchema()
# df.show()
# print(type(df))

# pandas_df = pd.read_csv("C:/Users/magnu/Downloads/pima-indians-diabetes.csv")
# print(type(pandas_df))

# # Exercise 2

# all_cols = ['Number of times pregnant', 'Body mass index', 'Plasma glucose concentration',
#             'Diastolic blood pressure', 'Triceps skinfold thickness', '2-Hour serum insulin',
#             'Diabetes pedigree function', 'Age', 'Class variable']
#
# df.select().describe().show() #Remember to give select an input.

# # TODO: groupBy().count() the relevant column and sort() it in the relevant order. Thereafter assign the x, bin and y values

# plt.hist(x, bins, histtype='bar', color='blue', weights=y)
# plt.xlabel('Pregnancies')
# plt.ylabel('Count')
# plt.show()

# # Exercise 3

# #Part 1

# features = df.rdd.map(lambda row: row[0:])
# corr_mat = Statistics.corr(features, method="") #Choose a method
# corr_df = pd.DataFrame(corr_mat)
# corr_df.index, corr_df.columns = x, y #TODO: Assign the correct x and y values

# print(corr_df.to_string())

# # Part 2

# df.select([count(when(isnull(c), c)).alias(c) for c in df.columns]).show()

# imputer = Imputer(inputCols=[""],
#                   outputCols=[""])
# imputer = imputer.setStrategy('').setMissingValue(np.nan)
# new_df = imputer.fit(object).transform(object)


# new_features = new_df.rdd.map(lambda row: row[0:])
# new_corr_mat = Statistics.corr(new_features, method="") #Choose a method
# new_corr_df = pd.DataFrame(new_corr_mat)
# new_corr_df.index, new_corr_df.columns = x, y #TODO: Assign the correct x and y values

# print(new_corr_df.to_string())