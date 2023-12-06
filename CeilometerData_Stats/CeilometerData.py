import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from stdout import *
pd.options.mode.chained_assignment = None  

class CeilometerData:
    def __init__(self, folder_path, folder_path_out):
        self.folder_path = folder_path
        self.folder_path_out = folder_path_out

    def list_csv_files(self):
        return [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]
    
    def merge_files_with_same_date(self):
        # sys.stdout = TextRedirector(self.output_text)
        csv_files = self.list_csv_files()

        if len(csv_files) == 0:
            print( "No CSV files found in the directory.\n")
            return

        date_pattern = re.compile(r"\d{2}\d{2}\d{2}")
        date_files_dict = {}

        for csv_file in csv_files:
            file_path = os.path.join(self.folder_path, csv_file)
            date_match = date_pattern.search(csv_file)
            if date_match:
                date = date_match.group()
                if date in date_files_dict:
                    date_files_dict[date].append(file_path)
                else:
                    date_files_dict[date] = [file_path]

        for date, files in date_files_dict.items():
            if len(files) > 1:
                merged_df = None
                for file_path in files:
                    df = pd.read_csv(file_path, delimiter=',')
                    if merged_df is None:
                        merged_df = df
                    else:
                        # Exclude titles from the second file
                        merged_df = pd.concat([merged_df, df[1:]], ignore_index=True)

                # Add 'merged' to the filename and save the file
                merged_filename = f"merged_{date}.csv"
                merged_filepath = os.path.join(self.folder_path, merged_filename)
                merged_df.to_csv(merged_filepath, index=False)
                print(f"Merged files for date {date} into {merged_filename}\n")

    def filter_filenames_with_unique_dates(self, filenames):
        merged_dates = set()
        filtered_filenames = []

        for filename in filenames:
            if "merged" in filename:
                date_match = re.search(r"\d{2}\d{2}\d{2}", filename)
                if date_match:
                    date = date_match.group()
                    merged_dates.add(date)

        for filename in filenames:
            date_match = re.search(r"\d{2}\d{2}\d{2}", filename)
            if not date_match or "merged" in filename or date_match.group() not in merged_dates:
                filtered_filenames.append(filename)

        return filtered_filenames

    def cloud_base(self, df):
        nan_string = "/////"
        percentage_nan_dict = {}
        total_cells_all_columns = 0
        total_nan_cells_all_columns = 0

        for col_num in range(1, 5):
            cloud_base_column = f"Cloud Base {col_num}( Meters )"
            nan_cells = df[cloud_base_column].eq(nan_string).sum()
            total_cells = df[cloud_base_column].size
            total_cells_all_columns += total_cells
            total_nan_cells_all_columns += nan_cells
            percentage_nan = (nan_cells / total_cells) * 100 if total_cells > 0 else 0
            percentage_nan_dict[cloud_base_column] = percentage_nan

        overall_percentage_nan = (total_nan_cells_all_columns / total_cells_all_columns) * 100 if total_cells_all_columns > 0 else 0
        percentage_nan_dict["Overall"] = overall_percentage_nan

        mask = df[[f"Cloud Base {col_num}( Meters )" for col_num in range(1, 5)]].apply(lambda row: all(cell == nan_string for cell in row), axis=1)

        clear_sky_df = df[mask]

        clear_sky_count = len(clear_sky_df)

        total_rows = len(df)
        clear_sky_percentage = (clear_sky_count / total_rows) * 100 if total_rows > 0 else 0
        percentage_nan_dict["Overall 2"] = clear_sky_percentage

        return percentage_nan_dict

    def process_csv_files(self):
        global csv_files
        self.merge_files_with_same_date()
        csv_files = self.list_csv_files()
        csv_files= self.filter_filenames_with_unique_dates(csv_files)
        print(f"{csv_files}\n")
        
        if len(csv_files) == 0:
            print( "No CSV files found in the directory.\n")
            return

        all_stats_df = pd.DataFrame()
        total_initial_rows = 0
        total_terminal_rows = 0

        for csv_file in csv_files:
            file_path = os.path.join(self.folder_path, csv_file)
            df = pd.read_csv(file_path, delimiter=',')
            initial_rows = len(df)
            # print(f"Initial rows: {initial_rows}")

            df['UTC Timestamp'] = pd.to_datetime(df['UTC Timestamp'])
            df['Hour'] = df['UTC Timestamp'].dt.hour
            df['Mixing Layer 3( Meters )'] = pd.to_numeric(df['Mixing Layer 3( Meters )'], errors='coerce')
            df['Mixing Layer 1( Meters )'] = pd.to_numeric(df['Mixing Layer 1( Meters )'], errors='coerce')
            df.loc[:, 'Thickness'] = df['Mixing Layer 3( Meters )'] - df['Mixing Layer 1( Meters )']

            df['date'] = pd.to_datetime(df['UTC Timestamp']).dt.strftime('%d%m%y')

            nan_string = "/////"
            mask = df[[f"Cloud Base {col_num}( Meters )" for col_num in range(1, 5)]].apply(lambda row: all(cell == nan_string for cell in row), axis=1)
            df_2 = df[mask]

            numeric_cols = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']

            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            for col in numeric_cols:
                df_2[col] = pd.to_numeric(df_2[col], errors='coerce')

            col_diff = df[numeric_cols[1]] - df[numeric_cols[0]]
            df_filter = df[abs(col_diff) > 500]

            final_rows = len(df_filter)
            # print(f"final rows: {final_rows}")

            df_filter['hour'] = df_filter['UTC Timestamp'].dt.hour
            unique_hours = df_filter['hour'].unique()

            date_pattern = re.compile(r"\d{2}\d{2}\d{2}")
            file_date_match = date_pattern.search(csv_file)
            if file_date_match:
                    file_date = file_date_match.group()
            print(f"Date: {file_date}:\t Initial rows: {initial_rows}\t / final rows: {final_rows}\t / hours: {unique_hours}\n")

            total_initial_rows += initial_rows
            total_terminal_rows += final_rows

            cloud_base_percentages = self.cloud_base(df)

            percentage1 = df['Sky Condition 1( Oktas )'].value_counts(normalize=True) * 100
            percentage2 = df['Sky Condition 2( Oktas )'].value_counts(normalize=True) * 100
            percentage3 = df['Sky Condition 3( Oktas )'].value_counts(normalize=True) * 100
            percentage4 = df['Sky Condition 4( Oktas )'].value_counts(normalize=True) * 100
            percentage5 = df['Sky Condition 5( Oktas )'].value_counts(normalize=True) * 100

            stats_dict = {
                'Type': 'General',
                'date': df_filter['date'].iloc[0] if len(df_filter) > 0 else None,
                'Sky Condition 1( Oktas ) Distribution': percentage1.to_dict(),
                'Sky Condition 2( Oktas ) Distribution': percentage2.to_dict(),
                'Sky Condition 3( Oktas ) Distribution': percentage3.to_dict(),
                'Sky Condition 4( Oktas ) Distribution': percentage4.to_dict(),
                'Sky Condition 5( Oktas ) Distribution': percentage5.to_dict(),
                **cloud_base_percentages
            }

            stats_df = pd.DataFrame([stats_dict])
            all_stats_df = pd.concat([all_stats_df, stats_df], ignore_index=True)
            df.to_csv(file_path, index=False)

        filename = 'statistics.csv'

        if not os.path.isfile(filename):
            open(filename, 'w').close()

        if os.path.isfile(filename) and os.path.getsize(filename) > 0:
            all_stats_df.to_csv(filename, mode='a', index=False, header=False)
        else:
            all_stats_df.to_csv(filename, mode='w', index=False)

        print(f"Total initial rows across all files: {total_initial_rows}")
        print(f"Total final rows across all files: {total_terminal_rows}")

        self.process_value_over_90()

    def process_value_over_90(self):
        df_s = pd.read_csv('statistics.csv', delimiter=',', dtype={'date': str})
        indices_value_over_90 = []

        for index, value in enumerate(df_s['Overall 2']):
            if value > 95:
                indices_value_over_90.append(index)

        mask = df_s.index.isin(indices_value_over_90)
        dates_value_over_90 = df_s.loc[mask, 'date']
        self.process_dates_value_over_90(df_s, dates_value_over_90) 

        return df_s, dates_value_over_90

    def check_date_in_filenames(self, date):
        matching_filenames = []
        date_pattern = re.compile(r"\d{2}\d{2}\d{2}")

        for filename in os.listdir(self.folder_path):
            if date_pattern.search(filename):
                if date in date_pattern.search(filename).group():
                    matching_filenames.append(filename)

        return matching_filenames
    
    def process_dates_value_over_90(self,df_s, dates_value_over_90):
        hourly_dfs = {hour: pd.DataFrame() for hour in range(24)}

        for date in dates_value_over_90:
            matching_filenames = self.check_date_in_filenames(date)
            if matching_filenames:
                print( f"Date {date} exists in filenames in the following files:\n")
                for filename in matching_filenames:
                    print(f"{filename}\n")

                for filename in matching_filenames:
                    file_path = os.path.join(self.folder_path, filename)
                    df = pd.read_csv(file_path, delimiter=',')

                    nan_string = "/////"
                    mask = df[[f"Cloud Base {col_num}( Meters )" for col_num in range(1, 5)]].apply(lambda row: all(cell == nan_string for cell in row), axis=1)
                    df_2 = df[mask]

                    numeric_cols = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']

                    for col in numeric_cols:
                        df_2.loc[:, col] = pd.to_numeric(df_2[col], errors='coerce')

                    col_diff = df[numeric_cols[1]] - df[numeric_cols[0]]
                    df_filter = df[abs(col_diff) > 500]

                    df_filter['UTC Timestamp'] = pd.to_datetime(df_filter['UTC Timestamp'], errors='coerce').copy()

                    df_filter['Mixing Layer 2( Meters )'] = pd.to_numeric(df_filter['Mixing Layer 2( Meters )'], errors='coerce').copy()
                    df_filter['Mixing Layer 3( Meters )'] = pd.to_numeric(df_filter['Mixing Layer 3( Meters )'], errors='coerce').copy()
                    df_filter.loc[:, 'hour'] = df_filter['UTC Timestamp'].dt.hour

                    df_filter = df_filter[['UTC Timestamp', 'hour', 'Mixing Layer 1( Meters )', 'Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']]

                    for hour in range(24):
                        hour_data = df_filter[df_filter['hour'] == hour]
                        hourly_dfs[hour] = pd.concat([hourly_dfs[hour], hour_data])

                for hour, hour_data in hourly_dfs.items():
                    output_path = os.path.join(self.folder_path_out, f"data_for_hour_{hour}.csv")
                    hour_data.to_csv(output_path, index=False)
            else:
                print(f"Date {date} does not exist in filenames.\n")

        n_valid_days = len(dates_value_over_90)
        n_total_days = len(csv_files)

        print(f"Total days: {n_total_days}, Valid days: {n_valid_days}\n")
        total_percentage = df_s['Overall 2'].sum() / len(df_s)
        print( f"monthly percentage of clear sky: {total_percentage:.2f}%\n")