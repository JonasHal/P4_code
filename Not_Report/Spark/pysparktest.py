# Exercise 1
# Initialize your Spark environement either locally or in cloud
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, isnull, when, col
from pyspark.mllib.stat import Statistics
from pyspark.ml.feature import Imputer

spark = SparkSession.builder.appName('BDS').getOrCreate()
#df = spark.read.csv("C:/Users/magnu/Downloads/pima-indians-diabetes.csv")
df1 = spark.read.options(header="True", inferSchema=True, delimiter=",") \
    .csv("C:/Users/magnu/Downloads/pima-indians-diabetes.csv")
#df1.printSchema()
num_cols = ['Number of times pregnant', 'Body mass index', 'Plasma glucose concentration',
            'Diastolic blood pressure', 'Triceps skinfold thickness', '2-Hour serum insulin',
            'Body mass index', 'Diabetes pedigree function', 'Age', 'Class variable']
#df1.select(num_cols).describe().show()
#df1.select([count(when(isnull(c), c)).alias(c) for c in df1.columns]).show()

test = df1.groupBy('Number of times pregnant').count()
sorted_test = test.sort(col('Number of times pregnant').asc())
#sorted_test.show(truncate=False)

x = sorted_test.select(col('Number of times pregnant')).toPandas()
y = sorted_test.select(col('count')).toPandas()
bins = np.arange(0, 17, 1)


plt.hist(x, bins, histtype='bar', color='blue', weights=y)
plt.xlabel('Pregnancies')
plt.ylabel('Count')
#plt.show()
# plt.bar(x=x, height=y)
# plt.show()

col_names = df1.columns
features = df1.rdd.map(lambda row: row[0:])
corr_mat = Statistics.corr(features, method="pearson")
corr_df = pd.DataFrame(corr_mat)
corr_df.index, corr_df.columns = col_names, col_names

print(corr_df.to_string())

imputer = Imputer(inputCols=["Plasma glucose concentration", "Diastolic blood pressure",
                             "Triceps skinfold thickness", "2-Hour serum insulin", "Body mass index"],
                  outputCols=["Plasma glucose concentration", "Diastolic blood pressure",
                             "Triceps skinfold thickness", "2-Hour serum insulin", "Body mass index"])
new_df = imputer.fit(df1)
new_df = new_df.transform(df1)

new_col_names = new_df.columns
features2 = new_df.rdd.map(lambda row: row[0:])
corr_mat2 = Statistics.corr(features2, method="pearson")
corr_df2 = pd.DataFrame(corr_mat2)
corr_df2.index, corr_df2.columns = new_col_names, new_col_names

print(corr_df2.to_string())

#imputer.fit(df1).transform(df1).show()
#imputer.setStrategy('median').setMissingValue(np.nan).fit(df1).transform(df1).show()