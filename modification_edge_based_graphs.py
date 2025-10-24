#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Edge-based Interactive Modification Graphs
Modified/Unmodified merkez node'larından elastic modulus improvement değerlerine bağlantılar
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

# MODIFIED GRAPH
print("\n🔨 Modified materyaller için edge-based graph oluşturuluyor...")
net_modified = Network(height='900px', width='100%', bgcolor='#222222', font_color='white')

# Fizik ayarları
net_modified.barnes_hut(gravity=-50000,
                       central_gravity=0.3,
                       spring_length=200,
                       spring_strength=0.01,
                       damping=0.09,
                       overlap=0)

# Merkez node: MODIFIED
net_modified.add_node("MODIFIED", 
                     color='#FFD700', 
                     size=50, 
                     title="Modified Materials",
                     label="MODIFIED",
                     font={'size': 20})

# Her modified materyal için elastic modulus improvement node'u ekle
for idx, row in df_modified.iterrows():
    improvement_log10 = row['Elastic modulus improvement Log10']
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    # Unique node ID
    node_id = f"EM_{idx}_{improvement_percent:.1f}%"
    
    # Node rengi - pozitif/negatif improvement'a göre
    color = '#4CAF50' if improvement_percent >= 0 else '#F44336'
    
    # Node boyutu - değere göre
    size = 15 + min(abs(improvement_log10) * 10, 35)
    
    # Hover text
    title = f"Elastic Modulus Improvement\n"
    title += f"Value: {improvement_percent:.1f}%\n"
    title += f"Log10: {improvement_log10:.4f}"
    
    # Node ekle
    net_modified.add_node(node_id, 
                         color=color, 
                         size=size, 
                         title=title, 
                         label=f"{improvement_percent:.1f}%")
    
    # Modified merkez node'undan bu değere edge ekle
    edge_title = f"Modified → {improvement_percent:.1f}%\n"
    edge_title += f"Log10: {improvement_log10:.4f}"
    
    net_modified.add_edge("MODIFIED", node_id,
                         width=2,
                         color='rgba(255, 215, 0, 0.3)',
                         title=edge_title)

# İnteraktif kontroller
net_modified.show_buttons(filter_=['physics'])

# HTML olarak kaydet
modified_html = os.path.join(output_dir, 'modified_edge_based_graph.html')
net_modified.save_graph(modified_html)
print(f"🌐 Modified edge-based graph kaydedildi: {modified_html}")

# UNMODIFIED GRAPH
print("\n🔨 Unmodified materyaller için edge-based graph oluşturuluyor...")
net_unmodified = Network(height='900px', width='100%', bgcolor='#222222', font_color='white')

# Fizik ayarları
net_unmodified.barnes_hut(gravity=-50000,
                         central_gravity=0.3,
                         spring_length=200,
                         spring_strength=0.01,
                         damping=0.09,
                         overlap=0)

# Merkez node: UNMODIFIED
net_unmodified.add_node("UNMODIFIED", 
                       color='#00CED1', 
                       size=50, 
                       title="Unmodified Materials",
                       label="UNMODIFIED",
                       font={'size': 20})

# Her unmodified materyal için elastic modulus improvement node'u ekle
for idx, row in df_unmodified.iterrows():
    improvement_log10 = row['Elastic modulus improvement Log10']
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    # Unique node ID
    node_id = f"EM_{idx}_{improvement_percent:.1f}%"
    
    # Node rengi - pozitif/negatif improvement'a göre
    color = '#2196F3' if improvement_percent >= 0 else '#FF9800'
    
    # Node boyutu - değere göre
    size = 15 + min(abs(improvement_log10) * 10, 35)
    
    # Hover text
    title = f"Elastic Modulus Improvement\n"
    title += f"Value: {improvement_percent:.1f}%\n"
    title += f"Log10: {improvement_log10:.4f}"
    
    # Node ekle
    net_unmodified.add_node(node_id, 
                           color=color, 
                           size=size, 
                           title=title, 
                           label=f"{improvement_percent:.1f}%")
    
    # Unmodified merkez node'undan bu değere edge ekle
    edge_title = f"Unmodified → {improvement_percent:.1f}%\n"
    edge_title += f"Log10: {improvement_log10:.4f}"
    
    net_unmodified.add_edge("UNMODIFIED", node_id,
                           width=2,
                           color='rgba(0, 206, 209, 0.3)',
                           title=edge_title)

# İnteraktif kontroller
net_unmodified.show_buttons(filter_=['physics'])

# HTML olarak kaydet
unmodified_html = os.path.join(output_dir, 'unmodified_edge_based_graph.html')
net_unmodified.save_graph(unmodified_html)
print(f"🌐 Unmodified edge-based graph kaydedildi: {unmodified_html}")

# COMBINED COMPARISON GRAPH
print("\n🔨 Karşılaştırmalı edge-based graph oluşturuluyor...")
net_combined = Network(height='900px', width='100%', bgcolor='#222222', font_color='white')

# Fizik ayarları - iki grubu ayırmak için
net_combined.barnes_hut(gravity=-30000,
                       central_gravity=0.1,
                       spring_length=300,
                       spring_strength=0.005,
                       damping=0.09,
                       overlap=0)

# İki merkez node
net_combined.add_node("MODIFIED", 
                     color='#FFD700', 
                     size=60, 
                     title="Modified Materials",
                     label="MODIFIED",
                     font={'size': 25},
                     x=-400, y=0)

net_combined.add_node("UNMODIFIED", 
                     color='#00CED1', 
                     size=60, 
                     title="Unmodified Materials",
                     label="UNMODIFIED",
                     font={'size': 25},
                     x=400, y=0)

# Modified değerlerini ekle (sol tarafa)
for idx, row in df_modified.head(50).iterrows():  # İlk 50 değer (çok fazla olmasın diye)
    improvement_percent = row['Elastic Modulus improvement (%)']
    improvement_log10 = row['Elastic modulus improvement Log10']
    
    node_id = f"M_{idx}"
    color = '#4CAF50' if improvement_percent >= 0 else '#F44336'
    
    net_combined.add_node(node_id, 
                         color=color, 
                         size=10,
                         title=f"Modified: {improvement_percent:.1f}%",
                         label=f"{improvement_percent:.0f}%",
                         x=-400 + np.random.randint(-200, 200),
                         y=np.random.randint(-300, 300))
    
    net_combined.add_edge("MODIFIED", node_id,
                         width=1,
                         color='rgba(255, 215, 0, 0.2)')

# Unmodified değerlerini ekle (sağ tarafa)
for idx, row in df_unmodified.head(50).iterrows():  # İlk 50 değer
    improvement_percent = row['Elastic Modulus improvement (%)']
    improvement_log10 = row['Elastic modulus improvement Log10']
    
    node_id = f"U_{idx}"
    color = '#2196F3' if improvement_percent >= 0 else '#FF9800'
    
    net_combined.add_node(node_id, 
                         color=color, 
                         size=10,
                         title=f"Unmodified: {improvement_percent:.1f}%",
                         label=f"{improvement_percent:.0f}%",
                         x=400 + np.random.randint(-200, 200),
                         y=np.random.randint(-300, 300))
    
    net_combined.add_edge("UNMODIFIED", node_id,
                         width=1,
                         color='rgba(0, 206, 209, 0.2)')

# İnteraktif kontroller
net_combined.show_buttons(filter_=['physics'])

# HTML olarak kaydet
combined_html = os.path.join(output_dir, 'combined_edge_based_graph.html')
net_combined.save_graph(combined_html)
print(f"🌐 Combined edge-based graph kaydedildi: {combined_html}")

# Özet istatistikler
print("\n📋 Özet İstatistikler:")
print(f"\nModified Materyaller ({len(df_modified)} adet):")
print(f"   - Ortalama improvement: {df_modified['Elastic Modulus improvement (%)'].mean():.1f}%")
print(f"   - Pozitif improvement: {(df_modified['Elastic Modulus improvement (%)'] > 0).sum()} adet")
print(f"   - Negatif improvement: {(df_modified['Elastic Modulus improvement (%)'] < 0).sum()} adet")

print(f"\nUnmodified Materyaller ({len(df_unmodified)} adet):")
print(f"   - Ortalama improvement: {df_unmodified['Elastic Modulus improvement (%)'].mean():.1f}%")
print(f"   - Pozitif improvement: {(df_unmodified['Elastic Modulus improvement (%)'] > 0).sum()} adet")
print(f"   - Negatif improvement: {(df_unmodified['Elastic Modulus improvement (%)'] < 0).sum()} adet")

print("\n✅ Edge-based interaktif grafikler başarıyla oluşturuldu!")