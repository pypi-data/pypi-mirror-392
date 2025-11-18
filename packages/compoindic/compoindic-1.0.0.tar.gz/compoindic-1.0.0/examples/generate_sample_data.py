"""
Generate Sample Data for Composite Indicator Builder
Author: Dr. Merwan Roudane

This script creates a sample Excel file that can be used to test the application.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def generate_sample_data(filename="sample_data.xlsx"):
    """Generate sample dataset for demonstration"""
    
    np.random.seed(42)
    
    # Countries
    countries = [
        'United States', 'Germany', 'Japan', 'United Kingdom', 'France',
        'Italy', 'Canada', 'Australia', 'Spain', 'Netherlands',
        'Sweden', 'Norway', 'Denmark', 'Finland', 'Belgium',
        'Switzerland', 'Austria', 'Ireland', 'New Zealand', 'Israel',
        'South Korea', 'Singapore', 'China', 'India', 'Brazil',
        'Mexico', 'Turkey', 'Poland', 'Czech Republic', 'Greece'
    ]
    
    n = len(countries)
    
    # Generate realistic data with some correlation structure
    base_development = np.random.uniform(0.5, 1.0, n)
    
    data = {
        'Country': countries,
        
        # Economic indicators
        'GDP_per_capita': 25000 + base_development * 50000 + np.random.normal(0, 5000, n),
        'Employment_Rate': 60 + base_development * 20 + np.random.normal(0, 3, n),
        'Innovation_Score': 30 + base_development * 50 + np.random.normal(0, 5, n),
        
        # Social indicators
        'Life_Expectancy': 70 + base_development * 12 + np.random.normal(0, 2, n),
        'Education_Index': 0.6 + base_development * 0.3 + np.random.normal(0, 0.05, n),
        'Healthcare_Quality': 50 + base_development * 40 + np.random.normal(0, 5, n),
        
        # Environmental indicators
        'Environmental_Performance': 40 + base_development * 40 + np.random.normal(0, 8, n),
        'Renewable_Energy_Share': 10 + base_development * 30 + np.random.normal(0, 5, n),
        
        # Governance indicators
        'Government_Effectiveness': 0.4 + base_development * 0.5 + np.random.normal(0, 0.1, n),
        'Corruption_Index': 30 + base_development * 50 + np.random.normal(0, 8, n)
    }
    
    df = pd.DataFrame(data)
    
    # Ensure values are within reasonable ranges
    df['GDP_per_capita'] = df['GDP_per_capita'].clip(lower=5000, upper=100000)
    df['Employment_Rate'] = df['Employment_Rate'].clip(lower=50, upper=85)
    df['Life_Expectancy'] = df['Life_Expectancy'].clip(lower=65, upper=85)
    df['Education_Index'] = df['Education_Index'].clip(lower=0.5, upper=1.0)
    df['Innovation_Score'] = df['Innovation_Score'].clip(lower=20, upper=90)
    df['Healthcare_Quality'] = df['Healthcare_Quality'].clip(lower=40, upper=95)
    df['Environmental_Performance'] = df['Environmental_Performance'].clip(lower=30, upper=90)
    df['Renewable_Energy_Share'] = df['Renewable_Energy_Share'].clip(lower=5, upper=60)
    df['Government_Effectiveness'] = df['Government_Effectiveness'].clip(lower=0.3, upper=1.0)
    df['Corruption_Index'] = df['Corruption_Index'].clip(lower=20, upper=90)
    
    # Round values
    df['GDP_per_capita'] = df['GDP_per_capita'].round(0)
    df['Employment_Rate'] = df['Employment_Rate'].round(1)
    df['Life_Expectancy'] = df['Life_Expectancy'].round(1)
    df['Education_Index'] = df['Education_Index'].round(3)
    df['Innovation_Score'] = df['Innovation_Score'].round(1)
    df['Healthcare_Quality'] = df['Healthcare_Quality'].round(1)
    df['Environmental_Performance'] = df['Environmental_Performance'].round(1)
    df['Renewable_Energy_Share'] = df['Renewable_Energy_Share'].round(1)
    df['Government_Effectiveness'] = df['Government_Effectiveness'].round(3)
    df['Corruption_Index'] = df['Corruption_Index'].round(1)
    
    # Save to Excel
    output_path = Path(__file__).parent / filename
    df.to_excel(output_path, index=False)
    
    print(f"Sample data generated successfully!")
    print(f"File saved to: {output_path}")
    print(f"\nData summary:")
    print(f"  Number of countries: {len(df)}")
    print(f"  Number of indicators: {len(df.columns) - 1}")
    print(f"\nIndicators:")
    for col in df.columns[1:]:
        print(f"  - {col}")
    print(f"\nYou can now use this file with the Composite Indicator Builder!")
    print(f"\nTo view the data:")
    print(df.head(10).to_string())
    
    return df


if __name__ == "__main__":
    df = generate_sample_data()
