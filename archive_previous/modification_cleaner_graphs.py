#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleaner Interactive Modification Graphs
Modified graph'ını daha düzenli hale getiren versiyon
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
df['Elastic modulus improvement Log10'] = pd.to_numeric(df['Elastic modulus improvement Log10'], errors='coerce')
df['Elastic Modulus improvement (%)'] = pd.to_numeric(df['Elastic Modulus improvement (%)'], errors='coerce')

# Modification kolonunu temizle
df['Modification (modified/unmodified)'] = df['Modification (modified/unmodified)'].str.strip().str.lower()

# NaN değerleri temizle
df_clean = df.dropna(subset=['Elastic modulus improvement Log10', 
                             'Elastic Modulus improvement (%)',
                             'Modification (modified/unmodified)'])

# Modified ve Unmodified materyalleri ayır
df_modified = df_clean[df_clean['Modification (modified/unmodified)'] == 'modified'].copy()
df_unmodified = df_clean[df_clean['Modification (modified/unmodified)'] == 'unmodified'].copy()

print(f"✅ Toplam {len(df_clean)} temiz veri noktası yüklendi")
print(f"   - Modified: {len(df_modified)}")
print(f"   - Unmodified: {len(df_unmodified)}")

# Output klasörü
output_dir = 'modification_interactive_output'
os.makedirs(output_dir, exist_ok=True)

# MODIFIED GRAPH - Temizlenmiş versiyon
print("\n🔨 Modified materyaller için temizlenmiş graph oluşturuluyor...")

# Modified datayı örnekle (çok fazla node olmasın)
sample_size = min(100, len(df_modified))  # Max 100 node
df_modified_sample = df_modified.sample(n=sample_size, random_state=42)

net_modified = Network(height='900px', width='100%', bgcolor='#1a1a1a', font_color='white')

# Daha güçlü fizik ayarları - dağılımı iyileştirmek için
net_modified.barnes_hut(
    gravity=-80000,           # Daha güçlü itme
    central_gravity=0.01,     # Zayıf merkez çekimi
    spring_length=300,        # Uzun spring'ler
    spring_strength=0.008,    # Zayıf spring gücü
    damping=0.09,
    overlap=0.5
)

# Merkez node: MODIFIED
net_modified.add_node("MODIFIED", 
                     color='#FFD700', 
                     size=60, 
                     title="Modified Materials",
                     label="MODIFIED",
                     font={'size': 25, 'color': 'white'},
                     x=0, y=0,  # Merkeze sabitli
                     physics=False)  # Merkez hareket etmesin

# Yüzde değerlerinin aralığını hesapla
percent_min = df_modified_sample['Elastic Modulus improvement (%)'].min()
percent_max = df_modified_sample['Elastic Modulus improvement (%)'].max()
percent_range = percent_max - percent_min

print(f"   Örneklem yüzde aralığı: [{percent_min:.1f}%, {percent_max:.1f}%]")

# Dairesel yerleşim için açı hesapla
angles = np.linspace(0, 2*np.pi, len(df_modified_sample), endpoint=False)

# Her materyal için node ekle
for i, (idx, row) in enumerate(df_modified_sample.iterrows()):
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    # Node ID
    node_id = f"M{i}"
    
    # Node rengi
    color = '#4CAF50' if improvement_percent >= 0 else '#F44336'
    
    # Node boyutu
    size = 15 + min(abs(improvement_percent) / 10, 25)
    
    # Uzaklık hesapla - yüzde değerine göre
    if percent_range > 0:
        normalized_distance = (improvement_percent - percent_min) / percent_range
    else:
        normalized_distance = 0.5
    
    # Minimum ve maksimum uzaklık
    min_distance = 200
    max_distance = 600
    distance = min_distance + normalized_distance * (max_distance - min_distance)
    
    # Dairesel konumlandırma
    angle = angles[i]
    x = distance * np.cos(angle)
    y = distance * np.sin(angle)
    
    # Hover text
    title = f"Modified Material\n"
    title += f"Improvement: {improvement_percent:.1f}%\n"
    title += f"Distance from center: {distance:.0f}"
    
    # Node ekle
    net_modified.add_node(node_id,
                         color=color,
                         size=size,
                         title=title,
                         label=f"{improvement_percent:.0f}%",
                         x=x, y=y,
                         font={'size': 10, 'color': 'white'})
    
    # Edge ekle
    edge_color = 'rgba(255, 215, 0, 0.2)'  # Şeffaf altın rengi
    
    net_modified.add_edge("MODIFIED", node_id,
                         width=1,
                         color=edge_color,
                         title=f"Improvement: {improvement_percent:.1f}%")

# HTML olarak kaydet
modified_html = os.path.join(output_dir, 'modified_clean_graph.html')
net_modified.save_graph(modified_html)
print(f"🌐 Modified temizlenmiş graph kaydedildi: {modified_html}")

# UNMODIFIED GRAPH - Aynı mantıkla
print("\n🔨 Unmodified materyaller için graph oluşturuluyor...")

net_unmodified = Network(height='900px', width='100%', bgcolor='#1a1a1a', font_color='white')

# Fizik ayarları
net_unmodified.barnes_hut(
    gravity=-50000,
    central_gravity=0.01,
    spring_length=250,
    spring_strength=0.01,
    damping=0.09,
    overlap=0.5
)

# Merkez node: UNMODIFIED
net_unmodified.add_node("UNMODIFIED", 
                       color='#00CED1', 
                       size=50, 
                       title="Unmodified Materials",
                       label="UNMODIFIED",
                       font={'size': 20, 'color': 'white'},
                       x=0, y=0,
                       physics=False)

# Yüzde değerlerinin aralığını hesapla
percent_min_u = df_unmodified['Elastic Modulus improvement (%)'].min()
percent_max_u = df_unmodified['Elastic Modulus improvement (%)'].max()
percent_range_u = percent_max_u - percent_min_u

print(f"   Yüzde aralığı: [{percent_min_u:.1f}%, {percent_max_u:.1f}%]")

# Dairesel yerleşim
angles_u = np.linspace(0, 2*np.pi, len(df_unmodified), endpoint=False)

# Her materyal için node ekle
for i, (idx, row) in enumerate(df_unmodified.iterrows()):
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    node_id = f"U{i}"
    color = '#2196F3' if improvement_percent >= 0 else '#FF9800'
    size = 15 + min(abs(improvement_percent) / 10, 25)
    
    # Uzaklık hesapla
    if percent_range_u > 0:
        normalized_distance = (improvement_percent - percent_min_u) / percent_range_u
    else:
        normalized_distance = 0.5
    
    distance = 150 + normalized_distance * 350
    
    # Konum hesapla
    angle = angles_u[i]
    x = distance * np.cos(angle)
    y = distance * np.sin(angle)
    
    title = f"Unmodified Material\n"
    title += f"Improvement: {improvement_percent:.1f}%\n"
    title += f"Distance from center: {distance:.0f}"
    
    net_unmodified.add_node(node_id,
                           color=color,
                           size=size,
                           title=title,
                           label=f"{improvement_percent:.0f}%",
                           x=x, y=y,
                           font={'size': 10, 'color': 'white'})
    
    # Edge ekle
    edge_color = 'rgba(0, 206, 209, 0.3)'
    
    net_unmodified.add_edge("UNMODIFIED", node_id,
                           width=1,
                           color=edge_color,
                           title=f"Improvement: {improvement_percent:.1f}%")

# HTML olarak kaydet
unmodified_html = os.path.join(output_dir, 'unmodified_clean_graph.html')
net_unmodified.save_graph(unmodified_html)
print(f"🌐 Unmodified temizlenmiş graph kaydedildi: {unmodified_html}")

# Özet istatistikler
print("\n📋 Temizlenmiş Graph İstatistikleri:")
print(f"\nModified Graph:")
print(f"   - Gösterilen node sayısı: {len(df_modified_sample)} (toplam {len(df_modified)} içinden)")
print(f"   - Yüzde aralığı: {percent_min:.1f}% - {percent_max:.1f}%")
print(f"   - Dairesel yerleşim kullanıldı")

print(f"\nUnmodified Graph:")
print(f"   - Node sayısı: {len(df_unmodified)}")
print(f"   - Yüzde aralığı: {percent_min_u:.1f}% - {percent_max_u:.1f}%")
print(f"   - Dairesel yerleşim kullanıldı")

print("\n✅ Temizlenmiş interaktif grafikler başarıyla oluşturuldu!")
print("📌 Özellikler:")
print("   - Modified graph örneklenmiş (iç içe geçme önlendi)")
print("   - Dairesel yerleşim ile düzenli dağılım")
print("   - Yüzde değerine göre merkez uzaklığı")
print("   - Sabit merkez node'lar")