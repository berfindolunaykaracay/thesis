#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Modification-based Elastic Modulus Network Graphs
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

def create_modification_graph(df_data, modification_type, color_scheme):
    """
    Belirli bir modification tipine göre graph oluşturur
    """
    print(f"\n🔨 {modification_type.capitalize()} materyaller için graph oluşturuluyor...")
    
    # NetworkX Graph
    G = nx.Graph()
    
    # Her satır için node ekle
    for idx, row in df_data.iterrows():
        # Log10 ve yüzde değerleri
        improvement_log10 = row['Elastic modulus improvement Log10']
        improvement_percent = row['Elastic Modulus improvement (%)']
        
        # Node ID'si - unique olması için index kullan
        node_id = f"{modification_type}_{idx}"
        
        # Node ekle
        G.add_node(node_id,
                   node_type=modification_type,
                   improvement_log10=improvement_log10,
                   improvement_percent=improvement_percent,
                   color=color_scheme['positive'] if improvement_percent >= 0 else color_scheme['negative'],
                   size=20 + min(abs(improvement_log10) * 10, 40),
                   label=f"{improvement_percent:.1f}%")
    
    # Tüm node'lar arasında bağlantılar oluştur (threshold kullanarak)
    nodes = list(G.nodes(data=True))
    distance_threshold = 0.5  # Log10 değerlerindeki yakınlık threshold'u
    
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            node1_id, node1_data = nodes[i]
            node2_id, node2_data = nodes[j]
            
            # Log10 değerleri arasındaki farkı hesapla
            distance = abs(node1_data['improvement_log10'] - node2_data['improvement_log10'])
            
            # Yakın değerler arasında bağlantı oluştur
            if distance < distance_threshold:
                G.add_edge(node1_id, node2_id,
                          weight=1 / (distance + 0.1),  # Yakın olanlar daha güçlü bağlantı
                          distance=distance,
                          color='lightgray')
    
    print(f"   - Node sayısı: {G.number_of_nodes()}")
    print(f"   - Edge sayısı: {G.number_of_edges()}")
    
    # PyVis ile interaktif görselleştirme
    print(f"🎨 {modification_type.capitalize()} için interaktif görselleştirme oluşturuluyor...")
    net = Network(height='900px', width='100%', bgcolor='#222222', font_color='white')
    
    # Fizik ayarları
    net.barnes_hut(gravity=-30000,
                   central_gravity=0.3,
                   spring_length=150,
                   spring_strength=0.01,
                   damping=0.09,
                   overlap=0)
    
    # Node'ları ekle
    for node_id, data in G.nodes(data=True):
        color = data.get('color', 'gray')
        size = data.get('size', 20)
        improvement_log10 = data.get('improvement_log10', 0)
        improvement_percent = data.get('improvement_percent', 0)
        label = data.get('label', '')
        
        # Hover text
        title = f"Elastic Modulus Improvement\n"
        title += f"Percentage: {improvement_percent:.1f}%\n"
        title += f"Log10: {improvement_log10:.4f}\n"
        title += f"Type: {modification_type.capitalize()}"
        
        net.add_node(node_id, color=color, size=size, title=title, label=label)
    
    # Edge'leri ekle
    for source, target, data in G.edges(data=True):
        distance = data.get('distance', 0)
        weight = data.get('weight', 1)
        
        edge_title = f"Log10 Distance: {distance:.4f}\n"
        edge_title += f"Connection Strength: {weight:.2f}"
        
        net.add_edge(source, target,
                    width=min(weight * 2, 5),
                    color='rgba(150, 150, 150, 0.3)',
                    title=edge_title)
    
    # İnteraktif kontroller ekle
    net.show_buttons(filter_=['physics'])
    
    # HTML olarak kaydet
    html_path = os.path.join(output_dir, f'{modification_type}_elastic_modulus_graph.html')
    net.save_graph(html_path)
    print(f"🌐 {modification_type.capitalize()} graph kaydedildi: {html_path}")
    
    return G, html_path

# Modified materyaller için graph oluştur
modified_colors = {
    'positive': '#4CAF50',  # Yeşil
    'negative': '#F44336'   # Kırmızı
}
G_modified, modified_html = create_modification_graph(df_modified, 'modified', modified_colors)

# Unmodified materyaller için graph oluştur  
unmodified_colors = {
    'positive': '#2196F3',  # Mavi
    'negative': '#FF9800'   # Turuncu
}
G_unmodified, unmodified_html = create_modification_graph(df_unmodified, 'unmodified', unmodified_colors)

# Karşılaştırmalı graph oluştur
print("\n🔨 Karşılaştırmalı graph oluşturuluyor...")
G_combined = nx.Graph()

# Modified materyalleri ekle
for idx, row in df_modified.iterrows():
    improvement_log10 = row['Elastic modulus improvement Log10']
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    node_id = f"modified_{idx}"
    G_combined.add_node(node_id,
                       node_type='modified',
                       improvement_log10=improvement_log10,
                       improvement_percent=improvement_percent,
                       color='#4CAF50' if improvement_percent >= 0 else '#F44336',
                       size=20,
                       label=f"M: {improvement_percent:.0f}%")

# Unmodified materyalleri ekle
for idx, row in df_unmodified.iterrows():
    improvement_log10 = row['Elastic modulus improvement Log10']
    improvement_percent = row['Elastic Modulus improvement (%)']
    
    node_id = f"unmodified_{idx}"
    G_combined.add_node(node_id,
                       node_type='unmodified',
                       improvement_log10=improvement_log10,
                       improvement_percent=improvement_percent,
                       color='#2196F3' if improvement_percent >= 0 else '#FF9800',
                       size=20,
                       label=f"U: {improvement_percent:.0f}%")

# PyVis ile karşılaştırmalı görselleştirme
print("🎨 Karşılaştırmalı interaktif görselleştirme oluşturuluyor...")
net_combined = Network(height='900px', width='100%', bgcolor='#222222', font_color='white')

# Fizik ayarları - farklı grupları ayırmak için
net_combined.barnes_hut(gravity=-40000,
                       central_gravity=0.1,
                       spring_length=250,
                       spring_strength=0.005,
                       damping=0.09,
                       overlap=0)

# Node'ları ekle
for node_id, data in G_combined.nodes(data=True):
    color = data.get('color', 'gray')
    size = data.get('size', 20)
    improvement_log10 = data.get('improvement_log10', 0)
    improvement_percent = data.get('improvement_percent', 0)
    node_type = data.get('node_type', '')
    label = data.get('label', '')
    
    # Hover text
    title = f"Elastic Modulus Improvement\n"
    title += f"Percentage: {improvement_percent:.1f}%\n"
    title += f"Log10: {improvement_log10:.4f}\n"
    title += f"Type: {node_type.capitalize()}"
    
    net_combined.add_node(node_id, color=color, size=size, title=title, label=label)

# İnteraktif kontroller ekle
net_combined.show_buttons(filter_=['physics'])

# HTML olarak kaydet
combined_html_path = os.path.join(output_dir, 'combined_modification_graph.html')
net_combined.save_graph(combined_html_path)
print(f"🌐 Karşılaştırmalı graph kaydedildi: {combined_html_path}")

# Özet istatistikler
print("\n📋 Özet İstatistikler:")
print("\nModified Materyaller:")
print(f"   - Sayı: {len(df_modified)}")
print(f"   - Ortalama improvement: {df_modified['Elastic Modulus improvement (%)'].mean():.1f}%")
print(f"   - Ortalama Log10: {df_modified['Elastic modulus improvement Log10'].mean():.3f}")
print(f"   - Min/Max improvement: {df_modified['Elastic Modulus improvement (%)'].min():.1f}% / {df_modified['Elastic Modulus improvement (%)'].max():.1f}%")

print("\nUnmodified Materyaller:")
print(f"   - Sayı: {len(df_unmodified)}")
print(f"   - Ortalama improvement: {df_unmodified['Elastic Modulus improvement (%)'].mean():.1f}%")
print(f"   - Ortalama Log10: {df_unmodified['Elastic modulus improvement Log10'].mean():.3f}")
print(f"   - Min/Max improvement: {df_unmodified['Elastic Modulus improvement (%)'].min():.1f}% / {df_unmodified['Elastic Modulus improvement (%)'].max():.1f}%")

print("\n✅ Tüm interaktif grafikler başarıyla oluşturuldu!")
print(f"📁 Çıktı klasörü: {output_dir}/")