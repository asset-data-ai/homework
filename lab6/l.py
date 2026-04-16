import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('data(lab6).csv')
print("\n============================")
print("task1")
print("============================\n")

#1
print(f"Форма DataFrame: {df.shape}")
print("\nТипы данных:")
print(df.dtypes)
print("\nПропуски:")
print(df.isnull().sum())
print("\nПервые 5 строк:")
print(df.head())
print("\n============================")
print("task2")
print("============================\n")

#2
for col in df.columns:
    converted_col = pd.to_numeric(df[col], errors='coerce')
    if converted_col.notna().any():
        df[col] = converted_col
        mean_val = df[col].mean()
        df[col] = df[col].fillna(mean_val)
print(df.head())
print("\n============================")
print("task3")
print("============================\n")

#3
df['total_value'] = df['col_2'] * df['col_3']
df['double_stock'] = df['col_3'] * 2
df['log_price'] = np.log(df['col_2'])
w = ['col_1', 'col_2', 'col_3', 'total_value', 'double_stock', 'log_price']
print(df[w].head())
print("\n============================")
print("task4")
print("============================\n")
#%%

#4
q = df[(df['col_2'] > 500) & (df['col_7'] == 'Electronics')]
print(q.head())
print("\n============================")
print("task5")
print("============================\n")

#5
summary_table = df.groupby('col_7').agg({'col_2': ['mean', 'max'], 'col_3': 'sum'}).reset_index()
summary_table.columns = ['category', 'mean_price', 'max_price', 'total_quantity']
print(summary_table)
print("\n============================")
print("task6")
print("============================\n")

#6
target_cols = [f'col_{i}' for i in range(2, 12)]
subset = df[target_cols]
stats_df = subset.select_dtypes(include=[np.number]).agg(['mean', 'median', 'std']).T
stats_df = stats_df.reset_index()
stats_df.columns = ['column', 'mean', 'median', 'std']
print(stats_df)
print("\n============================")
print("task7")
print("============================\n")