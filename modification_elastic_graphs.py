import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Dataset path configuration
DATASET_PATH = "DATASET 1.xlsx"

# Load the dataset
df = pd.read_excel(DATASET_PATH)

# Check column names and data
print("Column names:")
print(df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Find the exact column names
modification_col = None
elastic_col = None

for col in df.columns:
    if 'modification' in col.lower():
        modification_col = col
    if 'elastic' in col.lower() and 'log10' in col.lower() and 'improvement' in col.lower():
        elastic_col = col

print(f"\nModification column: {modification_col}")
print(f"Elastic modulus column: {elastic_col}")

# Filter data for modified and unmodified
if modification_col and elastic_col:
    # Remove rows with missing values
    df_clean = df[[modification_col, elastic_col]].dropna()
    
    # Separate modified and unmodified data
    modified_data = df_clean[df_clean[modification_col].str.lower() == 'modified'][elastic_col]
    unmodified_data = df_clean[df_clean[modification_col].str.lower() == 'unmodified'][elastic_col]
    
    print(f"\nModified samples: {len(modified_data)}")
    print(f"Unmodified samples: {len(unmodified_data)}")
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Modified materials
    ax1.scatter(range(len(modified_data)), modified_data.values, alpha=0.6, s=50, color='darkblue')
    ax1.set_xlabel('Sample Index')
    ax1.set_ylabel('Elastic Modulus Improvement (Log10)')
    ax1.set_title('Modified Materials - Elastic Modulus Improvement (Log10)')
    ax1.grid(True, alpha=0.3)
    
    # Add mean line for modified
    mean_modified = modified_data.mean()
    ax1.axhline(y=mean_modified, color='red', linestyle='--', label=f'Mean: {mean_modified:.3f}')
    ax1.legend()
    
    # Plot 2: Unmodified materials
    ax2.scatter(range(len(unmodified_data)), unmodified_data.values, alpha=0.6, s=50, color='darkgreen')
    ax2.set_xlabel('Sample Index')
    ax2.set_ylabel('Elastic Modulus Improvement (Log10)')
    ax2.set_title('Unmodified Materials - Elastic Modulus Improvement (Log10)')
    ax2.grid(True, alpha=0.3)
    
    # Add mean line for unmodified
    mean_unmodified = unmodified_data.mean()
    ax2.axhline(y=mean_unmodified, color='red', linestyle='--', label=f'Mean: {mean_unmodified:.3f}')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('modified_vs_unmodified_scatter.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create a combined comparison plot
    plt.figure(figsize=(10, 8))
    
    # Box plot comparison
    plt.subplot(2, 1, 1)
    data_to_plot = [modified_data.values, unmodified_data.values]
    positions = [1, 2]
    
    box = plt.boxplot(data_to_plot, positions=positions, widths=0.6, patch_artist=True,
                      labels=['Modified', 'Unmodified'])
    
    # Color the boxes
    colors = ['lightblue', 'lightgreen']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    
    plt.ylabel('Elastic Modulus Improvement (Log10)')
    plt.title('Comparison of Elastic Modulus Improvement: Modified vs Unmodified')
    plt.grid(True, alpha=0.3)
    
    # Violin plot comparison
    plt.subplot(2, 1, 2)
    combined_df = pd.DataFrame({
        'Type': ['Modified'] * len(modified_data) + ['Unmodified'] * len(unmodified_data),
        'Elastic Modulus Improvement (Log10)': pd.concat([modified_data, unmodified_data]).values
    })
    
    sns.violinplot(data=combined_df, x='Type', y='Elastic Modulus Improvement (Log10)', 
                   palette={'Modified': 'lightblue', 'Unmodified': 'lightgreen'})
    plt.title('Distribution Comparison: Modified vs Unmodified')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('modified_vs_unmodified_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print statistics
    print("\n=== Statistics ===")
    print(f"Modified materials:")
    print(f"  Count: {len(modified_data)}")
    print(f"  Mean: {modified_data.mean():.3f}")
    print(f"  Std: {modified_data.std():.3f}")
    print(f"  Min: {modified_data.min():.3f}")
    print(f"  Max: {modified_data.max():.3f}")
    
    print(f"\nUnmodified materials:")
    print(f"  Count: {len(unmodified_data)}")
    print(f"  Mean: {unmodified_data.mean():.3f}")
    print(f"  Std: {unmodified_data.std():.3f}")
    print(f"  Min: {unmodified_data.min():.3f}")
    print(f"  Max: {unmodified_data.max():.3f}")