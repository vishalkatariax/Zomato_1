"""
Phase 1: Foundation and Data Preparation
Goal: Build a clean, reliable restaurant dataset for downstream recommendation logic.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional
import os

class DataPreprocessor:
    """Handles data loading, cleaning, and preprocessing for restaurant recommendation system."""
    
    def __init__(self, data_path: str = "data/zomato.csv"):
        self.data_path = data_path
        self.raw_data = None
        self.processed_data = None
        
    def load_data(self) -> pd.DataFrame:
        """Load raw restaurant data from CSV file."""
        try:
            self.raw_data = pd.read_csv(self.data_path)
            print(f"Loaded {len(self.raw_data)} records from {self.data_path}")
            return self.raw_data
        except FileNotFoundError:
            print(f"Data file {self.data_path} not found. Creating sample data...")
            return self._create_sample_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample restaurant data for testing."""
        sample_data = [
            {
                'name': 'Toit - Indiranagar',
                'location': 'Indiranagar',
                'cuisines': 'European, Asian',
                'rating': 4.5,
                'cost_for_two': 1500,
                'address': '12th Main Road, Indiranagar'
            },
            {
                'name': 'The Black Sheep - Koramangala',
                'location': 'Koramangala',
                'cuisines': 'American, Bar Food',
                'rating': 4.2,
                'cost_for_two': 1800,
                'address': '5th Cross, Koramangala'
            },
            {
                'name': 'Cafe Thulp - Bellandur',
                'location': 'Bellandur',
                'cuisines': 'Continental, Italian',
                'rating': 4.0,
                'cost_for_two': 1200,
                'address': '12th Main, Bellandur'
            },
            {
                'name': 'Málà Project - Manhattan',
                'location': 'Manhattan',
                'cuisines': 'Sichuan, Dry Pot',
                'rating': 4.8,
                'cost_for_two': 2500,
                'address': '123 E 23rd St, New York'
            }
        ]
        return pd.DataFrame(sample_data)
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and preprocess the restaurant data."""
        if self.raw_data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        df = self.raw_data.copy()
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['name', 'location'], keep='first')
        
        # Handle missing values
        df = df.dropna(subset=['name', 'location', 'rating', 'cost_for_two'])
        
        # Standardize cost format
        if 'cost_for_two' in df.columns:
            df['cost_for_two'] = df['cost_for_two'].apply(self._extract_cost)
        
        # Standardize rating format
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df = df[df['rating'].between(1, 5)]
        
        # Clean cuisines
        if 'cuisines' in df.columns:
            df['cuisines'] = df['cuisines'].apply(self._clean_cuisines)
        
        # Clean location names
        if 'location' in df.columns:
            df['location'] = df['location'].str.strip().str.title()
        
        self.processed_data = df
        print(f"Cleaned data: {len(df)} records remaining")
        return df
    
    def _extract_cost(self, cost_str) -> int:
        """Extract numeric cost from cost string."""
        if pd.isna(cost_str):
            return 0
        if isinstance(cost_str, (int, float)):
            return int(cost_str)
        
        # Extract numbers from string like "₹1500 for two" or "1500"
        numbers = re.findall(r'\d+', str(cost_str))
        return int(numbers[0]) if numbers else 0
    
    def _clean_cuisines(self, cuisine_str) -> str:
        """Clean and standardize cuisine strings."""
        if pd.isna(cuisine_str):
            return "Unknown"
        
        # Remove extra spaces and standardize separators
        cleaned = str(cuisine_str).strip()
        cleaned = re.sub(r'\s+', ', ', cleaned)
        cleaned = re.sub(r',\s*,', ', ', cleaned)
        
        return cleaned.title()
    
    def get_processed_data(self) -> pd.DataFrame:
        """Return the processed data."""
        if self.processed_data is None:
            raise ValueError("Data not processed. Call clean_data() first.")
        return self.processed_data
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics of the processed data."""
        if self.processed_data is None:
            return {}
        
        df = self.processed_data
        return {
            'total_restaurants': len(df),
            'unique_locations': df['location'].nunique(),
            'unique_cuisines': len(df['cuisines'].str.split(', ').explode().unique()),
            'avg_rating': df['rating'].mean(),
            'avg_cost': df['cost_for_two'].mean(),
            'locations': sorted(df['location'].unique().tolist()),
            'cuisine_types': sorted(df['cuisines'].str.split(', ').explode().unique().tolist())
        }

def main():
    """Main function to demonstrate Phase 1 data preparation."""
    processor = DataPreprocessor()
    
    # Load data
    data = processor.load_data()
    
    # Clean data
    clean_data = processor.clean_data()
    
    # Display summary
    summary = processor.get_data_summary()
    print("\n=== Data Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Save processed data
    if not os.path.exists('data'):
        os.makedirs('data')
    
    clean_data.to_csv('data/processed_restaurants.csv', index=False)
    print("\nProcessed data saved to data/processed_restaurants.csv")
    
    return clean_data

if __name__ == "__main__":
    main()
