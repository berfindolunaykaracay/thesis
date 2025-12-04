#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direct Strain to Failure Network Graph
Her Excel satırındaki Strain to Failure değerlerini ayrı node olarak kullanır
Distance-based edge uzunlukları ile interactive görselleştirme
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
df['Polymer matrix strain to failure'] = pd.to_numeric(df['Polymer matrix strain to failure'], errors='coerce')
df['Strain to failure improvement%'] = pd.to_numeric(df['Strain to failure improvement%'], errors='coerce')
df['Polymer matrix strain to failure Log10'] = pd.to_numeric(df['Polymer matrix strain to failure Log10'], errors='coerce')
df['Strain to failure improvement Log10'] = pd.to_numeric(df['Strain to failure improvement Log10'], errors='coerce')

# NaN değerleri temizle - Log10 kolonlarının da dolu olduğundan emin ol
df_clean = df.dropna(subset=['Polymer matrix strain to failure', 
                             'Strain to failure improvement%',
                             'Polymer matrix strain to failure Log10',
                             'Strain to failure improvement Log10'])
print(f"✅ {len(df_clean)} temiz veri noktası yüklendi")

# Output klasörü
output_dir = 'strain_direct_output'
os.makedirs(output_dir, exist_ok=True)

# NetworkX Graph oluştur
G = nx.Graph()

print("\n🔨 Graph oluşturuluyor...")

# Her satır için node ve edge ekle
for idx, row in df_clean.iterrows():
    # Orijinal değerler (görselleştirme için)
    strain_value = row['Polymer matrix strain to failure']
    improvement_value = row['Strain to failure improvement%']
    
    # Log10 değerleri (distance hesaplama için)
    strain_log10 = row['Polymer matrix strain to failure Log10']
    improvement_log10 = row['Strain to failure improvement Log10']
    
    # Strain node'u ekle
    strain_node = f"{strain_value:.3f}"
    G.add_node(strain_node, 
               node_type='strain',
               value=strain_value,
               log10_value=strain_log10,
               color='lightblue',
               size=10 + min(abs(strain_value) * 100, 30))  # Node boyutu değere göre
    
    # Improvement node'u ekle  
    improvement_node = f"{improvement_value:.1f}%"
    G.add_node(improvement_node,
               node_type='improvement', 
               value=improvement_value,
               log10_value=improvement_log10,
               color='lightgreen' if improvement_value >= 0 else 'lightcoral',
               size=10 + min(abs(improvement_value)/10, 30))  # Node boyutu değere göre
    
    # Euclidean distance hesapla - LOG10 DEĞERLERİ KULLAN
    euclidean_distance = np.sqrt(strain_log10**2 + improvement_log10**2)
    
    # İki node arasında edge oluştur
    G.add_edge(strain_node, improvement_node,
               weight=1,
               color='gray',
               row_index=idx,
               distance=euclidean_distance,
               original_strain=strain_value,
               original_improvement=improvement_value,
               log10_strain=strain_log10,
               log10_improvement=improvement_log10)

print(f"\n📊 Graph İstatistikleri:")
print(f"   - Node sayısı: {G.number_of_nodes()}")
print(f"   - Edge sayısı: {G.number_of_edges()}")

# Distance değerlerinin min-max'ını bul (uzaklık normalizasyonu için)
distances = [data['distance'] for _, _, data in G.edges(data=True)]
min_distance = min(distances)
max_distance = max(distances)
distance_range = max_distance - min_distance

print(f"   Distance aralığı: {min_distance:.4f} - {max_distance:.4f}")

# PyVis ile interaktif görselleştirme
print("\n🎨 İnteraktif görselleştirme oluşturuluyor...")
net = Network(height='1000px', width='100%', bgcolor='#222222', font_color='white')

# Fizik ayarları - basit yaklaşım
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
    log10_value = data.get('log10_value', 0)
    
    # Hover için title
    if node_type == 'strain':
        title = f"Polymer Matrix Strain to Failure: {value:.3f}\n"
        title += f"Log10 Value: {log10_value:.4f}"
    else:
        title = f"Strain to Failure Improvement: {value:.1f}%\n"
        title += f"Log10 Value: {log10_value:.4f}"
    
    net.add_node(node, color=color, size=size, title=title, label=node)

# Edge'leri PyVis'e ekle - distance-based length ile
for source, target, data in G.edges(data=True):
    distance = data.get('distance', 0)
    original_strain = data.get('original_strain', 0)
    original_improvement = data.get('original_improvement', 0)
    log10_strain = data.get('log10_strain', 0)
    log10_improvement = data.get('log10_improvement', 0)
    
    # Edge uzunluğunu distance'a göre ayarla
    # Min distance = min length (50), Max distance = max length (500)
    if distance_range > 0:
        normalized_distance = (distance - min_distance) / distance_range
    else:
        normalized_distance = 0.5
    
    edge_length = 50 + normalized_distance * 450  # 50-500 arasında
    
    # Edge için title (hover text)
    edge_title = f"Euclidean Distance (Log10 based): {distance:.4f}\n"
    edge_title += f"Edge Length: {edge_length:.0f}\n"
    edge_title += f"Original Values:\n"
    edge_title += f"  - Strain to Failure: {original_strain:.3f}\n"
    edge_title += f"  - Improvement: {original_improvement:.1f}%\n"
    edge_title += f"Log10 Values:\n"
    edge_title += f"  - Strain Log10: {log10_strain:.4f}\n"
    edge_title += f"  - Improvement Log10: {log10_improvement:.4f}\n"
    edge_title += f"Calculation: √({log10_strain:.4f}² + {log10_improvement:.4f}²)"
    
    # Edge width'i distance'a göre ayarla (ters orantılı - küçük distance = kalın edge)
    edge_width = max(0.5, 3 - (normalized_distance * 2))
    
    # Edge label olarak distance'ı ekle
    net.add_edge(source, target, 
                 width=edge_width, 
                 color='gray',
                 label=f"{distance:.3f}",
                 title=edge_title,
                 length=edge_length,  # Gerçek uzaklık ayarı
                 font={'color': 'white', 'size': 10})

# İnteraktif kontroller ekle
try:
    net.show_buttons(filter_=['physics'])
except:
    pass  # PyVis versiyonu ile uyumluluk sorunu varsa geç

# HTML olarak kaydet
html_path = os.path.join(output_dir, 'strain_direct_graph.html')
net.save_graph(html_path)
print(f"🌐 İnteraktif graph kaydedildi: {html_path}")

# Özet istatistikler
print("\n📋 Özet:")
print(f"   - Toplam veri noktası: {len(df_clean)}")
print(f"   - Strain to Failure aralığı: {df_clean['Polymer matrix strain to failure'].min():.3f} - {df_clean['Polymer matrix strain to failure'].max():.3f}")
print(f"   - İyileşme aralığı: {df_clean['Strain to failure improvement%'].min():.1f} - {df_clean['Strain to failure improvement%'].max():.1f}%")
print(f"   - Strain Log10 aralığı: {df_clean['Polymer matrix strain to failure Log10'].min():.4f} - {df_clean['Polymer matrix strain to failure Log10'].max():.4f}")
print(f"   - İyileşme Log10 aralığı: {df_clean['Strain to failure improvement Log10'].min():.4f} - {df_clean['Strain to failure improvement Log10'].max():.4f}")

print("\n✅ Strain to Failure graph oluşturma tamamlandı!")