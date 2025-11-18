"""
Useful pandas operations for data manipulation and analysis.
This module provides examples of common pandas operations including:
- Data creation and loading
- Data exploration
- Filtering and selection
- Grouping and aggregation
- Handling missing values
- Merging and reshaping
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

def create_sample_dataframe():
    """Create a sample DataFrame for demonstration."""
    df = pd.DataFrame({
        'A': np.random.rand(10),
        'B': np.random.randint(0, 10, 10),
        'C': pd.date_range('2023-01-01', periods=10),
        'D': pd.Categorical(['X', 'Y', 'Z', 'X', 'Y', 'Z', 'X', 'Y', 'Z', 'X']),
        'E': ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 
              'zeta', 'eta', 'theta', 'iota', 'kappa']
    })
    # Add some missing values
    df.loc[2:4, 'A'] = np.nan
    df.loc[7, 'E'] = None
    return df

def basic_exploration(df):
    """Demonstrate basic dataframe exploration methods."""
    print("=== Basic DataFrame Exploration ===")
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nDataFrame information:")
    print(df.info())
    
    print("\nSummary statistics:")
    print(df.describe(include='all'))
    
    print("\nColumn data types:")
    print(df.dtypes)
    
    print("\nCheck for missing values:")
    print(df.isna().sum())
    
    return {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'missing_values': df.isna().sum().to_dict()
    }

def filtering_and_selection(df):
    """Demonstrate filtering and selection operations."""
    print("=== Filtering and Selection ===")
    
    print("\nSelect column 'A':")
    print(df['A'])
    
    print("\nSelect multiple columns:")
    print(df[['A', 'B', 'E']])
    
    print("\nFilter rows where B > 5:")
    print(df[df['B'] > 5])
    
    print("\nFilter rows with complex condition (B > 5 and D == 'X'):")
    print(df[(df['B'] > 5) & (df['D'] == 'X')])
    
    print("\nSelect using .loc (label-based):")
    print(df.loc[2:4, ['A', 'B', 'E']])
    
    print("\nSelect using .iloc (position-based):")
    print(df.iloc[2:4, [0, 1, 4]])
    
    print("\nBoolean indexing with .loc:")
    print(df.loc[df['D'] == 'X', 'B'])

def handle_missing_data(df):
    """Demonstrate methods for handling missing data."""
    print("=== Handling Missing Data ===")
    
    print("\nDrop rows with any NaN values:")
    print(df.dropna())
    
    print("\nDrop rows with all NaN values:")
    print(df.dropna(how='all'))
    
    print("\nFill NaN values with 0:")
    print(df.fillna(0))
    
    print("\nFill NaN values with column mean:")
    print(df.fillna(df.mean(numeric_only=True)))
    
    print("\nFill NaN with different values per column:")
    print(df.fillna({'A': 0, 'E': 'Unknown'}))
    
    print("\nInterpolate missing values:")
    print(df.interpolate())

def grouping_and_aggregation(df):
    """Demonstrate grouping and aggregation operations."""
    print("=== Grouping and Aggregation ===")
    
    print("\nGroup by column D and get mean of numeric columns:")
    print(df.groupby('D').mean(numeric_only=True))
    
    print("\nGroup by column D and get multiple aggregations:")
    print(df.groupby('D').agg({'A': ['mean', 'std'], 'B': ['min', 'max']}))
    
    print("\nGroup by multiple columns:")
    print(df.groupby(['D', df['B'] > 5]).mean(numeric_only=True))
    
    print("\nGroup by with custom aggregation function:")
    print(df.groupby('D')['B'].agg(lambda x: x.max() - x.min()))
    
    print("\nPivot table:")
    pivot_df = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=20),
        'category': np.random.choice(['X', 'Y', 'Z'], 20),
        'product': np.random.choice(['P1', 'P2', 'P3', 'P4'], 20),
        'sales': np.random.randint(10, 100, 20)
    })
    print(pd.pivot_table(pivot_df, values='sales', index='category', 
                        columns='product', aggfunc='sum', fill_value=0))

def merging_and_joining(df):
    """Demonstrate merging and joining dataframes."""
    print("=== Merging and Joining DataFrames ===")
    
    # Create two sample dataframes
    df1 = pd.DataFrame({
        'key': ['A', 'B', 'C', 'D'],
        'value1': [1, 2, 3, 4]
    })
    
    df2 = pd.DataFrame({
        'key': ['B', 'D', 'E', 'F'],
        'value2': [5, 6, 7, 8]
    })
    
    print("\nInner join:")
    print(pd.merge(df1, df2, on='key'))
    
    print("\nLeft join:")
    print(pd.merge(df1, df2, on='key', how='left'))
    
    print("\nRight join:")
    print(pd.merge(df1, df2, on='key', how='right'))
    
    print("\nOuter join:")
    print(pd.merge(df1, df2, on='key', how='outer'))
    
    print("\nConcatenate vertically:")
    print(pd.concat([df1, df1]))
    
    print("\nConcatenate horizontally:")
    print(pd.concat([df1, df2.drop('key', axis=1)], axis=1))

def data_transformation(df):
    """Demonstrate data transformation operations."""
    print("=== Data Transformation ===")
    
    print("\nApply function to each element:")
    print(df['B'].apply(lambda x: x ** 2))
    
    print("\nMap values to new values:")
    print(df['D'].map({'X': 1, 'Y': 2, 'Z': 3}))
    
    print("\nOne-hot encoding categorical column:")
    print(pd.get_dummies(df['D']))
    
    print("\nBin continuous data into categories:")
    print(pd.cut(df['B'], bins=3, labels=['Small', 'Medium', 'Large']))
    
    print("\nReshape with melt (wide to long):")
    melted = pd.melt(df[['D', 'A', 'B']], id_vars=['D'])
    print(melted)
    
    print("\nPivot (long to wide):")
    print(melted.pivot(index='D', columns='variable', values='value'))

def time_series_operations():
    """Demonstrate time series operations."""
    print("=== Time Series Operations ===")
    
    # Create a time series
    dates = pd.date_range('2023-01-01', periods=100)
    ts = pd.Series(np.random.randn(len(dates)).cumsum(), index=dates)
    
    print("\nResample to monthly frequency (downsample):")
    print(ts.resample('M').mean())
    
    print("\nResample to 2-day frequency (downsample):")
    print(ts.resample('2D').mean())
    
    print("\nShift time series forward by 2 periods:")
    print(ts.shift(2).head())
    
    print("\nPercent change between periods:")
    print(ts.pct_change().head())
    
    print("\nRolling window calculations (7-day moving average):")
    print(ts.rolling(7).mean().head(10))
    
    print("\nExpanding window calculations (cumulative mean):")
    print(ts.expanding().mean().head(10))

def io_operations():
    """Demonstrate I/O operations with pandas."""
    print("=== I/O Operations ===")
    
    df = create_sample_dataframe()
    
    print("\nWrite to CSV:")
    df.to_csv("sample.csv")
    print("DataFrame written to 'sample.csv'")
    
    print("\nRead from CSV:")
    df_read = pd.read_csv("sample.csv", index_col=0)
    print(df_read.head())
    
    print("\nWrite to Excel:")
    df.to_excel("sample.xlsx", sheet_name='Sheet1')
    print("DataFrame written to 'sample.xlsx'")
    
    print("\nCSV from string:")
    csv_data = """
    A,B,C
    1,2,3
    4,5,6
    7,8,9
    """
    df_csv = pd.read_csv(StringIO(csv_data.strip()))
    print(df_csv)
    
    print("\nRead from JSON:")
    df_json = pd.read_json(df.to_json(orient='records'))
    print(df_json.head())

def main():
    """Run all pandas examples."""
    df = create_sample_dataframe()
    
    # Basic operations
    basic_exploration(df)
    filtering_and_selection(df)
    handle_missing_data(df)
    grouping_and_aggregation(df)
    merging_and_joining(df)
    data_transformation(df)
    time_series_operations()
    io_operations()
    
    print("\nPlotting example:")
    df.plot(x='C', y='A', kind='line', figsize=(10, 6))
    plt.title('Sample Time Series Plot')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
