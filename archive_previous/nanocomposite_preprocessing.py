"""
Nanocomposite Dataset Preprocessing for GraphReasoning
This module preprocesses the nanocomposite material properties dataset for graph analysis.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional

# Default dataset path - kolayca değiştirilebilir
DEFAULT_DATASET_PATH = 'DATASET 1.xlsx'

def load_nanocomposite_dataset(file_path: str = None) -> pd.DataFrame:
    """Load and clean the nanocomposite dataset."""
    if file_path is None:
        file_path = DEFAULT_DATASET_PATH
    df = pd.read_excel(file_path)
    
    # Remove empty rows (those without article names)
    df_clean = df.dropna(subset=['Article']).copy()
    
    # Clean column names
    df_clean.columns = [col.strip() for col in df_clean.columns]
    
    return df_clean

def extract_numerical_values(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and clean numerical columns."""
    numerical_cols = [
        'MMT weight%', 'MMT volume%', 
        'Polymer matrix elastic modulus (GPa)', 
        'Nanocomposite Elastic Modulus (GPa)',
        'Elastic Modulus improvement (%)',
        'Polymer matrix Strength (MPa)',
        'Nanocomposite Strength (MPa)', 
        'Strength improvement (%)',
        'Polymer matrix strain to failure',
        'Nanocomposite strain to failure',
        'Strain to failure improvement%'
    ]
    
    df_processed = df.copy()
    
    for col in numerical_cols:
        if col in df_processed.columns:
            # Convert to string first, then replace common issues
            df_processed[col] = df_processed[col].astype(str)
            df_processed[col] = df_processed[col].str.replace('?', '')
            df_processed[col] = df_processed[col].str.replace('nan', '')
            df_processed[col] = df_processed[col].str.replace('NaN', '')
            df_processed[col] = df_processed[col].str.strip()
            
            # Convert to numeric, errors='coerce' will make invalid entries NaN
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    
    return df_processed

def clean_categorical_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize categorical columns."""
    df_processed = df.copy()
    
    # Clean polymer matrix names
    if 'Polymer matrix name' in df_processed.columns:
        df_processed['Polymer matrix name'] = df_processed['Polymer matrix name'].str.strip()
        df_processed['Polymer matrix name'] = df_processed['Polymer matrix name'].str.replace(r'\s+', ' ', regex=True)
    
    # Standardize dispersion types
    if 'Dispersion(microcomposite/exfoliated/intercalated/agglomerated)' in df_processed.columns:
        dispersion_col = 'Dispersion(microcomposite/exfoliated/intercalated/agglomerated)'
        df_processed[dispersion_col] = df_processed[dispersion_col].str.lower().str.strip()
        
        # Standardize common variations
        dispersion_mapping = {
            'exfoliated/intercaleted': 'exfoliated/intercalated',
            'intercalated/exfoliation': 'intercalated/exfoliated',
            'intercalated/ exfoliated': 'intercalated/exfoliated',
            'exfoliated/intercalated ': 'exfoliated/intercalated',
            'intercalated/ partially exfoliated': 'intercalated/partially exfoliated',
            'mixed (mostly intercalated)': 'intercalated',
            'intercalated': 'intercalated',
            'partially exfoliated': 'partially exfoliated',
            'microcomposite': 'microcomposite',
            'exfoliated/intercalated': 'exfoliated/intercalated'
        }
        
        df_processed[dispersion_col] = df_processed[dispersion_col].replace(dispersion_mapping)
    
    # Clean material types
    if 'Thermoset? Thermoplastic? Elastomer?' in df_processed.columns:
        material_col = 'Thermoset? Thermoplastic? Elastomer?'
        df_processed[material_col] = df_processed[material_col].str.strip()
        df_processed[material_col] = df_processed[material_col].replace('?', np.nan)
    
    # Clean test methods
    if 'Test Method' in df_processed.columns:
        df_processed['Test Method'] = df_processed['Test Method'].str.strip()
        df_processed['Test Method'] = df_processed['Test Method'].str.replace(r'\s+', ' ', regex=True)
        df_processed['Test Method'] = df_processed['Test Method'].replace('?', np.nan)
    
    return df_processed

def create_material_relationships(df: pd.DataFrame) -> List[Dict]:
    """Extract relationships from the dataset for graph generation."""
    relationships = []
    
    for idx, row in df.iterrows():
        # Skip rows with missing critical data
        if pd.isna(row.get('Polymer matrix name')) or pd.isna(row.get('Article')):
            continue
            
        polymer = row['Polymer matrix name']
        article = row['Article']
        
        # Core relationships
        relationships.append({
            'source': article,
            'target': polymer,
            'relation': 'uses_polymer_matrix',
            'type': 'material_composition'
        })
        
        # MMT relationships
        if not pd.isna(row.get('MMT weight%')):
            relationships.append({
                'source': polymer,
                'target': 'MMT',
                'relation': f"contains_{row['MMT weight%']:.1f}_wt_percent",
                'type': 'composition',
                'weight': row['MMT weight%']
            })
        
        # Dispersion relationships
        dispersion = row.get('Dispersion(microcomposite/exfoliated/intercalated/agglomerated)')
        if pd.notna(dispersion) and dispersion != '?':
            relationships.append({
                'source': polymer,
                'target': dispersion,
                'relation': 'has_dispersion_type',
                'type': 'morphology'
            })
        
        # Material type relationships
        material_type = row.get('Thermoset? Thermoplastic? Elastomer?')
        if pd.notna(material_type) and material_type != '?':
            relationships.append({
                'source': polymer,
                'target': material_type,
                'relation': 'is_material_type',
                'type': 'classification'
            })
        
        # Test method relationships
        test_method = row.get('Test Method')
        if pd.notna(test_method) and test_method != '?':
            relationships.append({
                'source': article,
                'target': test_method,
                'relation': 'tested_with',
                'type': 'characterization'
            })
        
        # Property relationships
        elastic_modulus = row.get('Nanocomposite Elastic Modulus (GPa)')
        if pd.notna(elastic_modulus):
            property_node = f"Elastic_Modulus_{elastic_modulus:.2f}_GPa"
            relationships.append({
                'source': polymer,
                'target': property_node,
                'relation': 'has_elastic_modulus',
                'type': 'mechanical_property',
                'value': elastic_modulus
            })
        
        # Strength relationships
        strength = row.get('Nanocomposite Strength (MPa)')
        if pd.notna(strength):
            property_node = f"Strength_{strength:.2f}_MPa"
            relationships.append({
                'source': polymer,
                'target': property_node,
                'relation': 'has_strength',
                'type': 'mechanical_property',
                'value': strength
            })
    
    return relationships

def generate_material_text_descriptions(df: pd.DataFrame) -> List[str]:
    """Generate text descriptions for graph creation from GraphReasoning."""
    descriptions = []
    
    for idx, row in df.iterrows():
        if pd.isna(row.get('Polymer matrix name')) or pd.isna(row.get('Article')):
            continue
            
        parts = []
        
        # Base description
        polymer = row['Polymer matrix name']
        article = row['Article']
        parts.append(f"The research article '{article}' investigates {polymer} nanocomposite materials.")
        
        # MMT content
        if not pd.isna(row.get('MMT weight%')):
            parts.append(f"The nanocomposite contains {row['MMT weight%']:.1f} weight percent MMT.")
        
        # Material properties
        if not pd.isna(row.get('Nanocomposite Elastic Modulus (GPa)')):
            parts.append(f"The elastic modulus is {row['Nanocomposite Elastic Modulus (GPa)']} GPa.")
        
        if not pd.isna(row.get('Nanocomposite Strength (MPa)')):
            parts.append(f"The tensile strength is {row['Nanocomposite Strength (MPa)']} MPa.")
        
        # Dispersion
        dispersion = row.get('Dispersion(microcomposite/exfoliated/intercalated/agglomerated)')
        if pd.notna(dispersion) and dispersion != '?':
            parts.append(f"The MMT dispersion is characterized as {dispersion}.")
        
        # Material type
        material_type = row.get('Thermoset? Thermoplastic? Elastomer?')
        if pd.notna(material_type) and material_type != '?':
            parts.append(f"The polymer matrix is classified as a {material_type.lower()}.")
        
        # Test method
        test_method = row.get('Test Method')
        if pd.notna(test_method) and test_method != '?':
            parts.append(f"Mechanical properties were characterized using {test_method}.")
        
        descriptions.append(' '.join(parts))
    
    return descriptions

def get_dataset_statistics(df: pd.DataFrame) -> Dict:
    """Get comprehensive statistics about the dataset."""
    stats = {}
    
    # Basic info
    stats['total_entries'] = len(df)
    stats['unique_articles'] = df['Article'].nunique()
    stats['unique_polymers'] = df['Polymer matrix name'].nunique()
    
    # Property statistics
    numerical_cols = [
        'Nanocomposite Elastic Modulus (GPa)',
        'Nanocomposite Strength (MPa)',
        'MMT weight%'
    ]
    
    for col in numerical_cols:
        if col in df.columns:
            values = df[col].dropna()
            if len(values) > 0:
                stats[f'{col}_stats'] = {
                    'count': len(values),
                    'mean': values.mean(),
                    'std': values.std(),
                    'min': values.min(),
                    'max': values.max()
                }
    
    # Categorical distributions
    categorical_cols = [
        'Thermoset? Thermoplastic? Elastomer?',
        'Dispersion(microcomposite/exfoliated/intercalated/agglomerated)',
        'Test Method'
    ]
    
    for col in categorical_cols:
        if col in df.columns:
            value_counts = df[col].value_counts()
            stats[f'{col}_distribution'] = value_counts.to_dict()
    
    return stats

if __name__ == "__main__":
    # Load and process the dataset
    df = load_nanocomposite_dataset()
    df = extract_numerical_values(df)
    df = clean_categorical_data(df)
    
    # Generate statistics
    stats = get_dataset_statistics(df)
    print("Dataset Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Generate text descriptions
    descriptions = generate_material_text_descriptions(df)
    print(f"\nGenerated {len(descriptions)} material descriptions for graph creation.")
    
    # Generate relationships
    relationships = create_material_relationships(df)
    print(f"Extracted {len(relationships)} relationships from the dataset.")