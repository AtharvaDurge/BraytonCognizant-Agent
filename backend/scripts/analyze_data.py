import pandas as pd
import os

data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'train_FD001.txt')
cols = ['unit', 'cycle'] + [f'set{i}' for i in range(1, 4)] + [f's{i}' for i in range(1, 22)]

df = pd.read_csv(data_path, sep=' ', header=None, names=cols)

healthy_df = df[df['cycle'] <= 20]
baseline_stats = healthy_df.mean()

relevant_sensors = ['s2', 's3', 's4', 's7', 's8', 's9', 's11', 's12', 's14', 's15', 's17', 's20', 's21']

clean_stats = baseline_stats[relevant_sensors].dropna()

print(clean_stats)

clean_stats.to_csv('baseline_thresholds.csv')