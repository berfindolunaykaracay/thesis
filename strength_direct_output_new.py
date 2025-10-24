#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direct Strength Network Graph - 4 Separate Graphs
Her Excel satırındaki Strength değerlerini ayrı node olarak kullanır
4 farklı grup: 
1. Sol kolon pozitif, sağ kolon negatif
2. Her iki kolon da pozitif  
3. Sol kolon negatif, sağ kolon pozitif
4. Her iki kolon da negatif
Distance hesaplaması orijinal değerlerle yapılır (Log10 kullanılmaz)
"""

import pandas as pd
import networkx as nx
import numpy as np
from pyvis.network import Network
import os
import warnings
warnings.filterwarnings('ignore')

# Dataset path configuration
DATASET_PATH = "DATASET 1.xlsx"

# Excel dosyasını yükle
print("📊 Excel dosyası yükleniyor...")
df = pd.read_excel(DATASET_PATH)

# Sayısal sütunları dönüştür
df['Polymer matrix Strength (MPa)'] = pd.to_numeric(df['Polymer matrix Strength (MPa)'], errors='coerce')
df['Strength improvement (%)'] = pd.to_numeric(df['Strength improvement (%)'], errors='coerce')

# NaN değerleri temizle
df_clean = df.dropna(subset=['Polymer matrix Strength (MPa)', 'Strength improvement (%)'])
print(f"✅ {len(df_clean)} temiz veri noktası yüklendi")

# Output klasörü
output_dir = 'strength_direct_output_new'
os.makedirs(output_dir, exist_ok=True)

# 4 grup oluştur
groups = {
    'positive_negative': df_clean[(df_clean['Polymer matrix Strength (MPa)'] > 0) & 
                                  (df_clean['Strength improvement (%)'] < 0)],
    'positive_positive': df_clean[(df_clean['Polymer matrix Strength (MPa)'] > 0) & 
                                  (df_clean['Strength improvement (%)'] >= 0)],
    'negative_positive': df_clean[(df_clean['Polymer matrix Strength (MPa)'] < 0) & 
                                  (df_clean['Strength improvement (%)'] >= 0)],
    'negative_negative': df_clean[(df_clean['Polymer matrix Strength (MPa)'] < 0) & 
                                  (df_clean['Strength improvement (%)'] < 0)]
}

# Grup açıklamaları
group_descriptions = {
    'positive_negative': 'Pozitif Strength, Negatif İyileşme',
    'positive_positive': 'Pozitif Strength, Pozitif İyileşme',
    'negative_positive': 'Negatif Strength, Pozitif İyileşme',
    'negative_negative': 'Negatif Strength, Negatif İyileşme'
}

print("\n📊 Grup İstatistikleri:")
for group_name, group_df in groups.items():
    print(f"   {group_descriptions[group_name]}: {len(group_df)} veri noktası")

# Her grup için graph oluştur
for group_name, group_df in groups.items():
    if len(group_df) == 0:
        print(f"\n⚠️  {group_descriptions[group_name]} için veri bulunamadı, atlanıyor...")
        continue
        
    print(f"\n🔨 {group_descriptions[group_name]} için graph oluşturuluyor...")
    
    # NetworkX Graph oluştur
    G = nx.Graph()
    
    # Her satır için node ve edge ekle
    for idx, row in group_df.iterrows():
        # Orijinal değerler
        strength_value = row['Polymer matrix Strength (MPa)']
        improvement_value = row['Strength improvement (%)']
        
        # Strength node'u ekle
        strength_node = f"{strength_value:.2f} MPa"
        G.add_node(strength_node, 
                   node_type='strength',
                   value=strength_value,
                   color='lightblue' if strength_value > 0 else 'lightpink',
                   size=10 + min(abs(strength_value)/10, 30))  # Node boyutu değere göre
        
        # Improvement node'u ekle  
        improvement_node = f"{improvement_value:.1f}%"
        G.add_node(improvement_node,
                   node_type='improvement', 
                   value=improvement_value,
                   color='lightgreen' if improvement_value >= 0 else 'lightcoral',
                   size=10 + min(abs(improvement_value)/10, 30))  # Node boyutu değere göre
        
        # Euclidean distance hesapla - ORİJİNAL DEĞERLER KULLAN
        euclidean_distance = np.sqrt(strength_value**2 + improvement_value**2)
        
        # İki node arasında edge oluştur
        G.add_edge(strength_node, improvement_node,
                   weight=1,
                   color='gray',
                   row_index=idx,
                   distance=euclidean_distance,
                   original_strength=strength_value,
                   original_improvement=improvement_value)
    
    print(f"   - Node sayısı: {G.number_of_nodes()}")
    print(f"   - Edge sayısı: {G.number_of_edges()}")
    
    # Distance değerlerinin min-max'ını bul
    distances = [data['distance'] for _, _, data in G.edges(data=True)]
    if distances:
        min_distance = min(distances)
        max_distance = max(distances)
        distance_range = max_distance - min_distance
        print(f"   - Distance aralığı: {min_distance:.4f} - {max_distance:.4f}")
    else:
        min_distance = 0
        max_distance = 1
        distance_range = 1
    
    # PyVis ile interaktif görselleştirme
    print(f"   🎨 İnteraktif görselleştirme oluşturuluyor...")
    net = Network(height='1000px', width='100%', bgcolor='#222222', font_color='white')
    
    # Fizik ayarları
    net.barnes_hut(gravity=-8000,
                   central_gravity=0.3,
                   spring_length=200,
                   spring_strength=0.05,
                   damping=0.09,
                   overlap=0)
    
    # Node'ları PyVis'e ekle
    for node, data in G.nodes(data=True):
        color = data.get('color', 'gray')
        size = data.get('size', 15)
        node_type = data.get('node_type', 'unknown')
        value = data.get('value', 0)
        
        # Hover için title
        if node_type == 'strength':
            title = f"Polymer Matrix Strength: {value:.2f} MPa"
        else:
            title = f"Strength Improvement: {value:.1f}%"
        
        net.add_node(node, color=color, size=size, title=title, label=node)
    
    # Edge'leri PyVis'e ekle
    for source, target, data in G.edges(data=True):
        distance = data.get('distance', 0)
        original_strength = data.get('original_strength', 0)
        original_improvement = data.get('original_improvement', 0)
        
        # Edge uzunluğunu distance'a göre ayarla
        if distance_range > 0:
            normalized_distance = (distance - min_distance) / distance_range
        else:
            normalized_distance = 0.5
        
        edge_length = 50 + normalized_distance * 450  # 50-500 arasında
        
        # Edge için title (hover text)
        edge_title = f"Euclidean Distance: {distance:.4f}\n"
        edge_title += f"Edge Length: {edge_length:.0f}\n"
        edge_title += f"Original Values:\n"
        edge_title += f"  - Strength: {original_strength:.2f} MPa\n"
        edge_title += f"  - Improvement: {original_improvement:.1f}%\n"
        edge_title += f"Calculation: √({original_strength:.2f}² + {original_improvement:.1f}²)"
        
        # Edge width'i distance'a göre ayarla (ters orantılı)
        edge_width = max(0.5, 3 - (normalized_distance * 2))
        
        # Edge label olarak distance'ı ekle
        net.add_edge(source, target, 
                     width=edge_width, 
                     color='gray',
                     label=f"{distance:.2f}",
                     title=edge_title,
                     length=edge_length,
                     font={'color': 'white', 'size': 10})
    
    # İnteraktif kontroller ekle
    try:
        net.show_buttons(filter_=['physics'])
    except:
        pass
    
    # HTML olarak kaydet
    html_path = os.path.join(output_dir, f'{group_name}_graph.html')
    net.save_graph(html_path)
    print(f"   🌐 İnteraktif graph kaydedildi: {html_path}")
    
    # Grup özeti
    if len(group_df) > 0:
        print(f"\n   📋 {group_descriptions[group_name]} Özeti:")
        print(f"      - Veri noktası: {len(group_df)}")
        print(f"      - Strength aralığı: {group_df['Polymer matrix Strength (MPa)'].min():.2f} - {group_df['Polymer matrix Strength (MPa)'].max():.2f} MPa")
        print(f"      - İyileşme aralığı: {group_df['Strength improvement (%)'].min():.1f} - {group_df['Strength improvement (%)'].max():.1f}%")

print("\n✅ Tüm graph'lar başarıyla oluşturuldu!")
print(f"📁 Output klasörü: {output_dir}")