import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth


dataset = [['Milk', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
           ['Dill', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
           ['Milk', 'Apple', 'Kidney Beans', 'Eggs'],
           ['Milk', 'Unicorn', 'Corn', 'Kidney Beans', 'Yogurt'],
           ['Corn', 'Onion', 'Onion', 'Kidney Beans', 'Ice cream', 'Eggs']]

te = TransactionEncoder()
te_ary = te.fit(dataset).transform(dataset)
df = pd.DataFrame(te_ary, columns=te.columns_)

frequent_itemsets = fpgrowth(df, min_support=0.6, use_colnames=True)
print(frequent_itemsets.sort_values(by=['support','itemsets'], ascending=True))
### alternatively:
frequent_itemsets2 = apriori(df, min_support=0.6, use_colnames=True)
frequent_itemsets3 = fpmax(df, min_support=0.6, use_colnames=True)
print(frequent_itemsets2.sort_values(by=['support','itemsets'], ascending=True))
print(frequent_itemsets3.sort_values(by=['support','itemsets'], ascending=True))
