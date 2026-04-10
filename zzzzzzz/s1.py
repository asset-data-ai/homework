import pandas as pd

#1
df = pd.read_csv('bank_advanced_dataset.csv')
print(df.head())
print(f"Размер: {df.shape}")
print(df.dtypes)
print(df.isnull().sum())

#2
types_list = df['Account_Type'].unique().tolist()
regions_list = df['Region'].unique().tolist()

#3
ids_upper = df['Customer_ID'].str.upper().tolist()
id_lengths = [len(cid) for cid in ids_upper]
avg_id_len = sum(id_lengths) / len(id_lengths)

#4
top_customers = df[df['Credit_Score'] >= 750]
print(top_customers[['Customer_ID', 'Age', 'Balance']].head(10))

#5
df['net_worth'] = df['Balance'] - df['Loan_Amount']
print(df.nlargest(10, 'net_worth'))

#6
top_customers.to_csv('student1_top_customers.csv', index=False)

#7
search_res = df[df['Customer_ID'].str.contains("CUST_01")]
print(search_res[['Account_Type', 'Balance']])

#8
print(df.sort_values(by='Balance', ascending=False).head(10))
print(df.sort_values(by='Age', ascending=True).head(10))

#9
df['income_per_transaction'] = df['Income'] / (df['Transactions_Last_Month'] + 1)
print(df.nlargest(5, 'income_per_transaction'))

#10
online_gen = (row for _, row in df[df['Online_Banking'] == 1].iterrows())
for _ in range(20):
    client = next(online_gen)
    print(client[['Customer_ID', 'Balance', 'Transactions_Last_Month']])

