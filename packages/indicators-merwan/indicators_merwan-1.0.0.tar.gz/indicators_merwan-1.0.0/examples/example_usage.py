"""
Example Usage of Composite Indicator Builder
Author: Dr. Merwan Roudane

This script demonstrates how to use the package programmatically
without the GUI interface.
"""

import pandas as pd
import numpy as np
from indicator import (
    PCA_Calculation,
    EqualWeights,
    Entropy_Calculation,
    BOD_Calculation,
    GeometricMean,
    normalizar_dados
)


def create_sample_data():
    """Create sample data for demonstration"""
    np.random.seed(42)
    
    countries = [
        'USA', 'Germany', 'Japan', 'UK', 'France', 
        'Italy', 'Canada', 'Australia', 'Spain', 'Netherlands',
        'Sweden', 'Norway', 'Denmark', 'Finland', 'Belgium'
    ]
    
    data = {
        'Country': countries,
        'GDP_per_capita': np.random.uniform(30000, 70000, 15),
        'Life_Expectancy': np.random.uniform(75, 85, 15),
        'Education_Index': np.random.uniform(0.7, 0.95, 15),
        'Innovation_Score': np.random.uniform(40, 80, 15),
        'Environmental_Index': np.random.uniform(50, 90, 15)
    }
    
    return pd.DataFrame(data)


def main():
    """Main example function"""
    print("=" * 70)
    print("Composite Indicator Builder - Example Usage")
    print("Author: Dr. Merwan Roudane")
    print("=" * 70)
    print()
    
    # Create sample data
    print("1. Creating sample data...")
    df = create_sample_data()
    print(f"   Created data for {len(df)} countries with 5 indicators")
    print()
    
    # Display data
    print("2. Sample Data Preview:")
    print(df.head())
    print()
    
    # Normalize data
    print("3. Normalizing data...")
    data = pd.DataFrame()
    indicator_cols = ['GDP_per_capita', 'Life_Expectancy', 'Education_Index', 
                     'Innovation_Score', 'Environmental_Index']
    
    for col in indicator_cols:
        data[col] = normalizar_dados(df[col].tolist(), orientacao="Min")
    
    print("   Normalization complete (Min-Max, Min-oriented)")
    print()
    
    # Calculate using different methods
    methods = {
        'PCA': PCA_Calculation(data),
        'Equal Weights': EqualWeights(data),
        'Entropy': Entropy_Calculation(data),
        'BoD': BOD_Calculation(data),
        'Geometric Mean': GeometricMean(data)
    }
    
    print("4. Calculating composite indicators using multiple methods...")
    print()
    
    results_dict = {}
    for method_name, model in methods.items():
        print(f"   Calculating: {method_name}...")
        results = model.run()
        results_dict[method_name] = results
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    
    # Display results for each method
    for method_name, results in results_dict.items():
        print(f"\n{method_name}")
        print("-" * 70)
        
        # Create results dataframe
        results_df = pd.DataFrame([
            {
                'Country': df['Country'].iloc[i],
                'CI': results[i].ci,
                'Rank': 0  # Will be filled
            }
            for i in range(len(results))
        ])
        
        # Sort and add ranks
        results_df = results_df.sort_values('CI', ascending=False)
        results_df['Rank'] = range(1, len(results_df) + 1)
        results_df = results_df[['Rank', 'Country', 'CI']]
        
        # Display top 10
        print("\nTop 10 Countries:")
        print(results_df.head(10).to_string(index=False))
        
        # Display weights
        print(f"\nWeights: {[f'{w:.3f}' for w in results[0].weights]}")
        
        # Statistics
        ci_values = [r.ci for r in results]
        print(f"\nStatistics:")
        print(f"  Min:    {np.min(ci_values):.4f}")
        print(f"  Max:    {np.max(ci_values):.4f}")
        print(f"  Mean:   {np.mean(ci_values):.4f}")
        print(f"  Std:    {np.std(ci_values):.4f}")
    
    # Correlation analysis between methods
    print()
    print("=" * 70)
    print("CORRELATION ANALYSIS BETWEEN METHODS")
    print("=" * 70)
    print()
    
    # Create correlation matrix
    method_names = list(results_dict.keys())
    n_methods = len(method_names)
    corr_matrix = np.zeros((n_methods, n_methods))
    
    for i, method1 in enumerate(method_names):
        for j, method2 in enumerate(method_names):
            ci1 = [r.ci for r in results_dict[method1]]
            ci2 = [r.ci for r in results_dict[method2]]
            corr_matrix[i, j] = np.corrcoef(ci1, ci2)[0, 1]
    
    # Display correlation matrix
    corr_df = pd.DataFrame(
        corr_matrix,
        index=method_names,
        columns=method_names
    )
    
    print("Correlation Matrix (CI values):")
    print(corr_df.round(3).to_string())
    print()
    
    # Rank correlation
    print("\nSpearman Rank Correlation:")
    from scipy.stats import spearmanr
    
    for i, method1 in enumerate(method_names):
        for j, method2 in enumerate(method_names):
            if i < j:
                ci1 = [r.ci for r in results_dict[method1]]
                ci2 = [r.ci for r in results_dict[method2]]
                rank_corr, p_value = spearmanr(ci1, ci2)
                print(f"  {method1} vs {method2}: {rank_corr:.3f} (p={p_value:.4f})")
    
    print()
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    print()
    print("To use the GUI, run: indicator")
    print("Or: python -m indicator.gui")
    print()


if __name__ == "__main__":
    main()
