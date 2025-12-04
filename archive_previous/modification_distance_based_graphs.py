#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Distance-based Interactive Modification Graphs
Edge uzunlukları elastic modulus improvement log10 değerlerine göre ayarlanmış
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

def create_distance_based_graph(df_data, modification_type, center_color, node_colors):
    """
    Edge uzunluğu log10 değerine göre ayarlanmış graph oluşturur
    """
    print(f"\n🔨 {modification_type.capitalize()} materyaller için distance-based graph oluşturuluyor...")
    
    # NetworkX Graph
    G = nx.Graph()
    
    # Merkez node ekle
    center_node = modification_type.upper()
    G.add_node(center_node, 
               node_type='center',
               color=center_color,
               size=60)
    
    # Yüzde değerlerinin min ve max'ını bul (normalizasyon için)
    percent_min = df_data['Elastic Modulus improvement (%)'].min()
    percent_max = df_data['Elastic Modulus improvement (%)'].max()
    percent_range = percent_max - percent_min
    
    print(f"   Yüzde aralığı: [{percent_min:.1f}%, {percent_max:.1f}%]")
    
    # Her materyal için node ekle
    for idx, row in df_data.iterrows():
        improvement_log10 = row['Elastic modulus improvement Log10']
        improvement_percent = row['Elastic Modulus improvement (%)']
        
        # Unique node ID
        node_id = f"{modification_type[0].upper()}{idx}"
        
        # Node rengi
        color = node_colors['positive'] if improvement_percent >= 0 else node_colors['negative']
        
        # Node boyutu - yüzde değerine göre
        size = 10 + min(abs(improvement_percent) / 5, 30)
        
        # Edge uzunluğu - yüzde değerine göre normalize edilmiş
        # Negatif yüzde değerleri için mutlak değer al
        normalized_distance = abs(improvement_percent - percent_min) / percent_range if percent_range > 0 else 0.5
        edge_length = 100 + normalized_distance * 400  # 100 ile 500 arasında
        
        G.add_node(node_id,
                  node_type='improvement',
                  improvement_percent=improvement_percent,
                  improvement_log10=improvement_log10,
                  color=color,
                  size=size,
                  edge_length=edge_length)
        
        # Edge ekle - weight olarak uzunluk bilgisi
        G.add_edge(center_node, node_id,
                  weight=1/edge_length,  # Kısa edge'ler daha güçlü bağlantı
                  length=edge_length,
                  percent_value=improvement_percent)
    
    # PyVis network oluştur
    net = Network(height='900px', width='100%', bgcolor='#222222', font_color='white')
    
    # Fizik ayarları - edge uzunluklarını dikkate alacak şekilde
    net.repulsion(node_distance=200, spring_length=200, spring_strength=0.05)
    net.set_edge_smooth('discrete')
    
    # Node'ları ekle
    for node, data in G.nodes(data=True):
        node_type = data.get('node_type', 'unknown')
        
        if node_type == 'center':
            title = f"{modification_type.capitalize()} Materials Center"
            label = node
            size = data.get('size', 60)
        else:
            improvement_percent = data.get('improvement_percent', 0)
            improvement_log10 = data.get('improvement_log10', 0)
            edge_length = data.get('edge_length', 0)
            
            title = f"Elastic Modulus Improvement\n"
            title += f"Value: {improvement_percent:.1f}%\n"
            title += f"Log10: {improvement_log10:.4f}\n"
            title += f"Edge Length: {edge_length:.0f}"
            
            label = f"{improvement_percent:.0f}%"
            size = data.get('size', 15)
        
        net.add_node(node,
                    color=data.get('color', 'gray'),
                    size=size,
                    title=title,
                    label=label)
    
    # Edge'leri ekle
    for source, target, edge_data in G.edges(data=True):
        length = edge_data.get('length', 200)
        percent_value = edge_data.get('percent_value', 0)
        
        edge_title = f"Improvement: {percent_value:.1f}%\n"
        edge_title += f"Edge Length: {length:.0f}"
        
        # Edge rengi - yüzde değerine göre gradient
        if percent_value < 0:
            edge_color = 'rgba(255, 100, 100, 0.3)'  # Kırmızımsı (negatif)
        elif percent_value < 50:
            edge_color = 'rgba(255, 200, 100, 0.3)'  # Turuncumsu (düşük pozitif)
        elif percent_value < 100:
            edge_color = 'rgba(100, 255, 100, 0.3)'  # Yeşilimsi (orta)
        else:
            edge_color = 'rgba(100, 100, 255, 0.3)'  # Mavimsi (yüksek)
        
        net.add_edge(source, target,
                    width=2,
                    color=edge_color,
                    title=edge_title,
                    length=length)
    
    # İnteraktif kontroller
    net.show_buttons(filter_=['physics'])
    
    return net

# Modified graph oluştur
modified_colors = {
    'positive': '#4CAF50',
    'negative': '#F44336'
}
net_modified = create_distance_based_graph(df_modified, 'modified', '#FFD700', modified_colors)
modified_html = os.path.join(output_dir, 'modified_distance_based_graph.html')
net_modified.save_graph(modified_html)
print(f"🌐 Modified distance-based graph kaydedildi: {modified_html}")

# Unmodified graph oluştur
unmodified_colors = {
    'positive': '#2196F3',
    'negative': '#FF9800'
}
net_unmodified = create_distance_based_graph(df_unmodified, 'unmodified', '#00CED1', unmodified_colors)
unmodified_html = os.path.join(output_dir, 'unmodified_distance_based_graph.html')
net_unmodified.save_graph(unmodified_html)
print(f"🌐 Unmodified distance-based graph kaydedildi: {unmodified_html}")

# Özet istatistikler
print("\n📋 Edge Uzunluk İstatistikleri:")
print("\nModified Materyaller:")
percent_values_mod = df_modified['Elastic Modulus improvement (%)'].values
print(f"   - Min %: {percent_values_mod.min():.1f}% (En kısa edge)")
print(f"   - Max %: {percent_values_mod.max():.1f}% (En uzun edge)")
print(f"   - Ortalama %: {percent_values_mod.mean():.1f}%")

print("\nUnmodified Materyaller:")
percent_values_unmod = df_unmodified['Elastic Modulus improvement (%)'].values
print(f"   - Min %: {percent_values_unmod.min():.1f}% (En kısa edge)")
print(f"   - Max %: {percent_values_unmod.max():.1f}% (En uzun edge)")
print(f"   - Ortalama %: {percent_values_unmod.mean():.1f}%")

print("\n✅ Distance-based interaktif grafikler başarıyla oluşturuldu!")
print("📌 Edge uzunlukları yüzde değerlerine göre ayarlandı:")
print("   - Düşük % = Kısa edge (merkeze yakın)")
print("   - Yüksek % = Uzun edge (merkeze uzak)")