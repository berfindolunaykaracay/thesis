#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Interactive Modification-based Elastic Modulus Network Graphs
Modified ve Unmodified materyaller için ayrı interaktif grafikler oluşturur
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

# Modified materyaller için basit graph
print("\n🔨 Modified materyaller için graph oluşturuluyor...")
net_modified = Network(height='800px', width='100%', bgcolor='#f0f0f0')

# Her materyal için bir node ekle
for idx, row in df_modified.iterrows():
    improvement_log10 = row['Elastic modulus improvement Log10']
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    node_id = f"M{idx}"
    color = '#4CAF50' if improvement_percent >= 0 else '#F44336'
    size = 10 + min(abs(improvement_log10) * 5, 30)
    
    title = f"Modified Material\n"
    title += f"Improvement: {improvement_percent:.1f}%\n"
    title += f"Log10: {improvement_log10:.3f}"
    
    net_modified.add_node(node_id, 
                         color=color, 
                         size=size, 
                         title=title, 
                         label=f"{improvement_percent:.0f}%")

# Basit fizik ayarları
net_modified.repulsion(node_distance=120, spring_length=100)

# HTML olarak kaydet
modified_html = os.path.join(output_dir, 'modified_elastic_modulus_graph.html')
net_modified.save_graph(modified_html)
print(f"🌐 Modified graph kaydedildi: {modified_html}")

# Unmodified materyaller için basit graph
print("\n🔨 Unmodified materyaller için graph oluşturuluyor...")
net_unmodified = Network(height='800px', width='100%', bgcolor='#f0f0f0')

# Her materyal için bir node ekle
for idx, row in df_unmodified.iterrows():
    improvement_log10 = row['Elastic modulus improvement Log10']
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    node_id = f"U{idx}"
    color = '#2196F3' if improvement_percent >= 0 else '#FF9800'
    size = 10 + min(abs(improvement_log10) * 5, 30)
    
    title = f"Unmodified Material\n"
    title += f"Improvement: {improvement_percent:.1f}%\n"
    title += f"Log10: {improvement_log10:.3f}"
    
    net_unmodified.add_node(node_id, 
                           color=color, 
                           size=size, 
                           title=title, 
                           label=f"{improvement_percent:.0f}%")

# Basit fizik ayarları
net_unmodified.repulsion(node_distance=120, spring_length=100)

# HTML olarak kaydet
unmodified_html = os.path.join(output_dir, 'unmodified_elastic_modulus_graph.html')
net_unmodified.save_graph(unmodified_html)
print(f"🌐 Unmodified graph kaydedildi: {unmodified_html}")

# Özet istatistikler
print("\n📋 Özet İstatistikler:")
print("\nModified Materyaller:")
print(f"   - Sayı: {len(df_modified)}")
print(f"   - Ortalama improvement: {df_modified['Elastic Modulus improvement (%)'].mean():.1f}%")
print(f"   - Ortalama Log10: {df_modified['Elastic modulus improvement Log10'].mean():.3f}")

print("\nUnmodified Materyaller:")
print(f"   - Sayı: {len(df_unmodified)}")
print(f"   - Ortalama improvement: {df_unmodified['Elastic Modulus improvement (%)'].mean():.1f}%")
print(f"   - Ortalama Log10: {df_unmodified['Elastic modulus improvement Log10'].mean():.3f}")

print("\n✅ İnteraktif grafikler başarıyla oluşturuldu!")