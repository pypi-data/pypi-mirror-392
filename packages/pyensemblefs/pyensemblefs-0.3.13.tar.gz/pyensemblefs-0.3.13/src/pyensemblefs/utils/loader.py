from pathlib import Path
import os.path as path
import pandas as pd

PATH_PROJECT_RESULTS = Path("results")


def save_dataframe_results(df_results_current):
    PATH_PROJECT_RESULTS.mkdir(parents=True, exist_ok=True)
    results_name = df_results_current.attrs['results_name']
    path_results_file = Path.joinpath(PATH_PROJECT_RESULTS, '{}.csv'.format(results_name))

    if path.exists(str(path_results_file)):
        df_results_history = pd.read_csv(str(path_results_file))
        df_results_all = pd.concat([df_results_history, df_results_current], ignore_index=True)
        df_results_all.to_csv(str(path_results_file), index=False)
    else:
        df_results_current.to_csv(str(path_results_file), index=False)
