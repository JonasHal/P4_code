from pyspark.context import SparkContext
sc = SparkContext.getOrCreate()

raw = [(1,1), (2,2), (3, 3), (1, 4), (2, 5), (3, 6), (1, 7), (2, 8), (3, 9)]
tbl = [dict(zip(('a', 'b'), e)) for e in raw]

data = sc.parallelize(tbl)

sum_cnt = data.map(lambda x: (x['a'], (x['b'], 1))) \
    .reduceByKey(lambda x, y: (x[0]+y[0], x[1]+y[1])) \
    .collect()

res = [(x[0], x[1][0]/x[1][1]) for x in sum_cnt]
print(res)