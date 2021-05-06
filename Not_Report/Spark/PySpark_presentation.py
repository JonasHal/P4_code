import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, isnull, when, col
from pyspark.mllib.stat import Statistics
from pyspark.ml.feature import Imputer
import seaborn as sns

#Til Jonas
import os
import sys

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

spark = SparkSession.builder.appName('BDS').getOrCreate()
df1 = spark.read.options(header="True", inferSchema=True, delimiter=",") \
    .csv("C:/Users/jon12/Downloads/pima-indians-diabetes.csv")
# df1.printSchema()
# df1.show()
# print(type(df1))

# pandas_df = pd.read_csv("C:/Users/magnu/Downloads/pima-indians-diabetes.csv")
# print(type(pandas_df))

num_cols = ['Number of times pregnant', 'Body mass index', 'Plasma glucose concentration',
            'Diastolic blood pressure', 'Triceps skinfold thickness', '2-Hour serum insulin',
            'Diabetes pedigree function', 'Age', 'Class variable']

df1.select(num_cols).describe().show()
df1.select(num_cols).summary().show()

def histogram_count_pregnancies(df):
    df_count = df.groupBy('Number of times pregnant').count()
    df_count_sorted = df_count.sort(col('Number of times pregnant').asc())
    #df_count_sorted.show(truncate=False)

    x = df_count_sorted.select(col('Number of times pregnant')).toPandas()
    y = df_count_sorted.select(col('count')).toPandas()
    bins = np.arange(0, 17, 1)
    plt.hist(x, bins, histtype='bar', color='blue', weights=y)
    plt.xlabel('Pregnancies')
    plt.ylabel('Count')
    plt.show()

#histogram_count_pregnancies(df1)

def violin_age(df):
    x = df.select("2-Hour serum insulin").toPandas()

    sns.violinplot(data=x)
    plt.show()

#violin_age(df1)

def linechart_class_TST(df):
    df = df.sort("Age", ascending=True)

    df = df.withColumn('Age Group', when((col("Age") > 50), "Above 50")\
                                    .when((col("Age") < 30), "Under 30")\
                                    .otherwise("Between 30-50"))

    class_var = df.select("Class variable").toPandas()
    tst = df.select("Triceps skinfold thickness").toPandas()
    age_group = df.select("Age Group").toPandas()

    data = pd.concat([class_var, tst, age_group], axis=1, join="inner")

    sns.set()
    sns.pointplot(x="Age Group",
                  y="Triceps skinfold thickness",
                  hue="Class variable",
                  data=data,
                  capsize=0.2
                  )
    plt.show()

#linechart_class_TST(df1)

col_names = df1.columns
features = df1.rdd.map(lambda row: row[0:]) #PythonRDD[41] at RDD at PythonRDD.scale:54
corr_mat = Statistics.corr(features, method="pearson")

corr_df = pd.DataFrame(corr_mat)
corr_df.index, corr_df.columns = col_names, col_names

#print(corr_df.to_string())

df1.select([count(when(isnull(c), c)).alias(c) for c in df1.columns]).show()
#Vi tæller antal gange hvornår værdierne i c (kolonne) er null, i hver c. Det selecter vi, og renammer (alias) denne count
#til hvad end kolonnen c hedder. Det gøres i et for loop.

imputer = Imputer(inputCols=["Plasma glucose concentration", "Diastolic blood pressure",
                             "Triceps skinfold thickness", "2-Hour serum insulin", "Body mass index"],
                  outputCols=["Plasma glucose concentration", "Diastolic blood pressure",
                             "Triceps skinfold thickness", "2-Hour serum insulin", "Body mass index"])

imputer = imputer.setStrategy('median').setMissingValue(np.nan)
new_df = imputer.fit(df1).transform(df1)

new_col_names = new_df.columns
features2 = new_df.rdd.map(lambda row: row[0:])
corr_mat2 = Statistics.corr(features2, method="pearson")
corr_df2 = pd.DataFrame(corr_mat2)
corr_df2.index, corr_df2.columns = new_col_names, new_col_names

#print(corr_df2.to_string())

#imputer.fit(df1).transform(df1).show()
#imputer.setStrategy('median').setMissingValue(np.nan).fit(df1).transform(df1).show()

sns.set(style='ticks')
sns.pairplot(new_df.toPandas(),
             x_vars=["Body mass index", "Number of times pregnant", "Age"],
             y_vars=["Body mass index", "Number of times pregnant"],
             hue='Class variable', markers=["D", "o"])
#plt.show()
