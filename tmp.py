import pandas as pd

df = pd.read_csv('./prelim_results_sps.csv')
print(df[df['success'] == True])