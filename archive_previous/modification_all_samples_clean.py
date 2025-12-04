#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
All Samples Clean Interactive Modification Graphs
Tüm örnekleri gösterir ama temiz görüntü sağlar
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

def create_clean_all_samples_graph(df_data, modification_type, center_color, node_colors):
    """
    Tüm örnekleri temiz şekilde gösteren graph oluşturur
    """
    print(f"\n🔨 {modification_type.capitalize()} materyaller için tüm örnekli temiz graph oluşturuluyor...")
    
    # PyVis network - büyük boyut
    net = Network(height='1000px', width='100%', bgcolor='#0d1117', font_color='white')
    
    # Çok güçlü fizik ayarları - yayılmayı artırmak için
    net.set_options("""
    {
        "nodes": {
            "font": {"size": 8},
            "borderWidth": 1,
            "borderWidthSelected": 2
        },
        "edges": {
            "color": {"inherit": false},
            "smooth": {"enabled": false},
            "width": 1.5,
            "arrows": {"to": {"enabled": false}}
        },
        "physics": {
            "enabled": true,
            "solver": "repulsion",
            "repulsion": {
                "nodeDistance": 300,
                "centralGravity": 0.001,
                "springLength": 400,
                "springConstant": 0.001,
                "damping": 0.09
            }
        },
        "layout": {
            "improvedLayout": true
        }
    }
    """)
    
    # Merkez node
    center_node = modification_type.upper()
    net.add_node(center_node,
                 color=center_color,
                 size=80,
                 title=f"{modification_type.capitalize()} Materials",
                 label=center_node,
                 font={'size': 30, 'color': 'white'},
                 borderWidth=3,
                 x=0, y=0,
                 physics=False)
    
    # Yüzde değerlerini kategorilere ayır (daha organize görünüm için)
    df_sorted = df_data.sort_values('Elastic Modulus improvement (%)')
    
    # Yüzde aralıklarını hesapla
    percent_min = df_sorted['Elastic Modulus improvement (%)'].min()
    percent_max = df_sorted['Elastic Modulus improvement (%)'].max()
    percent_range = percent_max - percent_min
    
    print(f"   Yüzde aralığı: [{percent_min:.1f}%, {percent_max:.1f}%]")
    print(f"   Toplam {len(df_sorted)} node ekleniyor...")
    
    # Spiral yerleşim parametreleri
    spiral_turns = 8  # Daha fazla tur
    max_radius = 800  # Daha büyük maksimum yarıçap
    min_radius = 150  # Minimum yarıçap
    
    # Her materyal için node ekle
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        improvement_percent = row['Elastic Modulus improvement (%)']
        
        # Node ID - unique olsun
        node_id = f"{modification_type[0].upper()}_{i}_{improvement_percent:.0f}"
        
        # Node rengi - daha belirgin renkler
        if improvement_percent >= 100:
            color = '#00FF00'  # Parlak yeşil (çok yüksek)
        elif improvement_percent >= 50:
            color = node_colors['positive']  # Normal yeşil/mavi
        elif improvement_percent >= 0:
            color = '#FFFF00'  # Sarı (düşük pozitif)
        else:
            color = node_colors['negative']  # Kırmızı/turuncu
        
        # Node boyutu - daha küçük ama görünür
        size = 8 + min(abs(improvement_percent) / 20, 15)
        
        # Spiral konumlandırma
        progress = i / len(df_sorted)  # 0-1 arası ilerleme
        
        # Yarıçap hesapla - yüzde değerine göre
        if percent_range > 0:
            normalized_value = (improvement_percent - percent_min) / percent_range
        else:
            normalized_value = 0.5
        
        radius = min_radius + normalized_value * (max_radius - min_radius)
        
        # Açı hesapla - spiral için
        angle = progress * spiral_turns * 2 * np.pi
        
        # Konum hesapla
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        # Hover text - kısa tutulmuş
        title = f"{improvement_percent:.1f}%"
        
        # Label - çok kısa
        label = f"{improvement_percent:.0f}%"
        
        # Node ekle
        net.add_node(node_id,
                     color=color,
                     size=size,
                     title=title,
                     label=label,
                     x=x, y=y,
                     font={'size': 6, 'color': 'white'})
        
        # Edge ekle - daha belirgin
        # Edge rengi - yüzde değerine göre
        if improvement_percent >= 100:
            edge_color = 'rgba(0, 255, 0, 0.4)'     # Parlak yeşil
        elif improvement_percent >= 50:
            edge_color = 'rgba(76, 175, 80, 0.4)'   # Yeşil
        elif improvement_percent >= 0:
            edge_color = 'rgba(255, 255, 0, 0.4)'   # Sarı
        else:
            edge_color = 'rgba(244, 67, 54, 0.4)'   # Kırmızı
        
        # Edge kalınlığı - değere göre
        edge_width = max(0.5, min(abs(improvement_percent) / 100, 3))
        
        net.add_edge(center_node, node_id,
                     width=edge_width,
                     color=edge_color,
                     title=f"{improvement_percent:.1f}%")
    
    return net

# Modified graph oluştur - tüm örneklerle
modified_colors = {
    'positive': '#4CAF50',
    'negative': '#F44336'
}

net_modified = create_clean_all_samples_graph(df_modified, 'modified', '#FFD700', modified_colors)
modified_html = os.path.join(output_dir, 'modified_all_samples_clean.html')
net_modified.save_graph(modified_html)
print(f"🌐 Modified tüm örnekli graph kaydedildi: {modified_html}")

# Unmodified graph oluştur - tüm örneklerle
unmodified_colors = {
    'positive': '#2196F3',
    'negative': '#FF9800'
}

net_unmodified = create_clean_all_samples_graph(df_unmodified, 'unmodified', '#00CED1', unmodified_colors)
unmodified_html = os.path.join(output_dir, 'unmodified_all_samples_clean.html')
net_unmodified.save_graph(unmodified_html)
print(f"🌐 Unmodified tüm örnekli graph kaydedildi: {unmodified_html}")

# Bonus: Kompakt görüntü için cluster-based versiyon
print("\n🔨 Cluster-based kompakt versiyonlar oluşturuluyor...")

def create_clustered_graph(df_data, modification_type, center_color, node_colors):
    """
    Benzer değerleri cluster halinde gösteren versiyon
    """
    net = Network(height='900px', width='100%', bgcolor='#1a1a1a', font_color='white')
    
    # Fizik ayarları
    net.repulsion(node_distance=200, spring_length=300, spring_strength=0.02)
    
    # Merkez node
    center_node = modification_type.upper()
    net.add_node(center_node,
                 color=center_color,
                 size=60,
                 title=f"{modification_type.capitalize()} Materials ({len(df_data)} samples)",
                 label=f"{center_node}\n({len(df_data)})",
                 font={'size': 16, 'color': 'white'},
                 x=0, y=0,
                 physics=False)
    
    # Değerleri 10'luk gruplara böl
    df_data['percent_group'] = (df_data['Elastic Modulus improvement (%)'] // 10) * 10
    groups = df_data.groupby('percent_group')
    
    # Her grup için bir cluster node
    angles = np.linspace(0, 2*np.pi, len(groups), endpoint=False)
    
    for i, (group_value, group_data) in enumerate(groups):
        count = len(group_data)
        avg_percent = group_data['Elastic Modulus improvement (%)'].mean()
        
        # Cluster node
        cluster_id = f"{modification_type}_cluster_{group_value:.0f}"
        
        # Renk
        color = node_colors['positive'] if avg_percent >= 0 else node_colors['negative']
        
        # Boyut - grup büyüklüğüne göre
        size = 15 + min(count * 2, 40)
        
        # Konum
        distance = 200 + abs(group_value) / 5
        angle = angles[i]
        x = distance * np.cos(angle)
        y = distance * np.sin(angle)
        
        # Hover text
        title = f"Range: {group_value:.0f}% - {group_value+10:.0f}%\n"
        title += f"Samples: {count}\n"
        title += f"Avg: {avg_percent:.1f}%"
        
        net.add_node(cluster_id,
                     color=color,
                     size=size,
                     title=title,
                     label=f"{group_value:.0f}%+\n({count})",
                     x=x, y=y,
                     font={'size': 10, 'color': 'white'})
        
        # Edge
        net.add_edge(center_node, cluster_id,
                     width=min(count/5, 5),
                     color='rgba(200, 200, 200, 0.5)')
    
    return net

# Clustered versiyonları oluştur
net_modified_cluster = create_clustered_graph(df_modified, 'modified', '#FFD700', modified_colors)
modified_cluster_html = os.path.join(output_dir, 'modified_clustered.html')
net_modified_cluster.save_graph(modified_cluster_html)
print(f"🌐 Modified clustered graph kaydedildi: {modified_cluster_html}")

net_unmodified_cluster = create_clustered_graph(df_unmodified, 'unmodified', '#00CED1', unmodified_colors)
unmodified_cluster_html = os.path.join(output_dir, 'unmodified_clustered.html')
net_unmodified_cluster.save_graph(unmodified_cluster_html)
print(f"🌐 Unmodified clustered graph kaydedildi: {unmodified_cluster_html}")

# Özet
print("\n📋 Tüm Örnekli Graph İstatistikleri:")
print(f"\nModified Graph:")
print(f"   - Toplam node: {len(df_modified)} + 1 merkez")
print(f"   - Spiral yerleşim kullanıldı")
print(f"   - 4 farklı renk kategorisi")

print(f"\nUnmodified Graph:")  
print(f"   - Toplam node: {len(df_unmodified)} + 1 merkez")
print(f"   - Spiral yerleşim kullanıldı")
print(f"   - 4 farklı renk kategorisi")

print("\n✅ Tüm versiyonlar başarıyla oluşturuldu!")
print("📌 Oluşturulan dosyalar:")
print("   - modified_all_samples_clean.html (tüm 646 örnek)")
print("   - unmodified_all_samples_clean.html (tüm 82 örnek)")
print("   - modified_clustered.html (gruplar halinde)")
print("   - unmodified_clustered.html (gruplar halinde)")