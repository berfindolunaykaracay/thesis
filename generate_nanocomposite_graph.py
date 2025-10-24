#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nanocomposite Excel Verilerinden Graph Oluşturma
Bu script Excel dosyanızdaki verileri kullanarak bilgi grafiği oluşturur.
"""

import pandas as pd
import networkx as nx
import os
import warnings
warnings.filterwarnings('ignore')

# Dataset dosya yolu - kolayca değiştirilebilir
DATASET_PATH = "DATASET 1.xlsx"

# Excel dosyasını yükle
print(f"📊 Excel dosyası yükleniyor: {DATASET_PATH}")
df = pd.read_excel(DATASET_PATH)

# Gereksiz sütunu kaldır
if 'Unnamed: 18' in df.columns:
    df = df.drop('Unnamed: 18', axis=1)

# Veriyi temizle
df_clean = df.dropna(subset=['MMT weight%', 'Polymer matrix name'])
print(f"✅ {len(df_clean)} temiz veri noktası yüklendi")

# Output klasörünü oluştur
output_dir = 'nanocomposite_output'
os.makedirs(output_dir, exist_ok=True)

# NetworkX Graph oluştur
G = nx.Graph()

print("\n🔨 Graph oluşturuluyor...")

# 1. Polimer düğümleri ekle
polymers = df_clean['Polymer matrix name'].unique()
for polymer in polymers:
    if polymer and polymer != '?':
        G.add_node(polymer, node_type='polymer', color='lightblue', size=20)

# 2. MMT modifikasyon düğümleri ekle
modifications = df_clean['Modification (modified/unmodified)'].unique()
for mod in modifications:
    if mod and mod != '?':
        G.add_node(mod, node_type='modification', color='lightgreen', size=15)

# 3. Dispersiyon tipi düğümleri ekle
dispersions = df_clean['Dispersion(microcomposite/exfoliated/intercalated/agglomerated)'].unique()
for disp in dispersions:
    if disp and disp != '?':
        G.add_node(disp, node_type='dispersion', color='lightyellow', size=15)

# 4. Polimer tipi düğümleri ekle
polymer_types = df_clean['Thermoset? Thermoplastic? Elastomer?'].unique()
for ptype in polymer_types:
    if ptype and ptype != '?':
        G.add_node(ptype, node_type='polymer_type', color='lightcoral', size=18)

# 5. İlişkileri (edges) ekle
print("🔗 İlişkiler ekleniyor...")

for idx, row in df_clean.iterrows():
    polymer = row['Polymer matrix name']
    mod = row['Modification (modified/unmodified)']
    disp = row['Dispersion(microcomposite/exfoliated/intercalated/agglomerated)']
    ptype = row['Thermoset? Thermoplastic? Elastomer?']
    mmt_weight = row['MMT weight%']
    
    # Polimer - Modifikasyon ilişkisi
    if polymer and polymer != '?' and mod and mod != '?':
        if G.has_node(polymer) and G.has_node(mod):
            G.add_edge(polymer, mod, 
                      relation='has_modification', 
                      weight=mmt_weight,
                      color='green')
    
    # Polimer - Dispersiyon ilişkisi
    if polymer and polymer != '?' and disp and disp != '?':
        if G.has_node(polymer) and G.has_node(disp):
            G.add_edge(polymer, disp, 
                      relation='has_dispersion',
                      weight=mmt_weight,
                      color='blue')
    
    # Polimer - Polimer tipi ilişkisi
    if polymer and polymer != '?' and ptype and ptype != '?':
        if G.has_node(polymer) and G.has_node(ptype):
            G.add_edge(polymer, ptype,
                      relation='is_type',
                      weight=1,
                      color='red')

# Performans verilerine göre önemli düğümler ekle
print("📈 Performans düğümleri ekleniyor...")

# Sayısal sütunları dönüştür
df_clean['Elastic Modulus improvement (%)'] = pd.to_numeric(df_clean['Elastic Modulus improvement (%)'], errors='coerce')
df_clean['Strength improvement (%)'] = pd.to_numeric(df_clean['Strength improvement (%)'], errors='coerce')

# Yüksek performanslı malzemeler
high_performance = df_clean[df_clean['Elastic Modulus improvement (%)'] > 100].dropna(subset=['Elastic Modulus improvement (%)'])
if len(high_performance) > 0:
    G.add_node('High Elastic Performance', node_type='performance', color='gold', size=25)
    for idx, row in high_performance.iterrows():
        polymer = row['Polymer matrix name']
        if polymer and polymer != '?' and G.has_node(polymer):
            G.add_edge(polymer, 'High Elastic Performance',
                      relation='achieves',
                      improvement=row['Elastic Modulus improvement (%)'],
                      color='gold')

# Graph istatistikleri
print(f"\n📊 Graph İstatistikleri:")
print(f"- Düğüm sayısı: {G.number_of_nodes()}")
print(f"- Kenar sayısı: {G.number_of_edges()}")
print(f"- Bağlantılı bileşen sayısı: {nx.number_connected_components(G)}")

# Graphı kaydet
print("\n💾 Graph kaydediliyor...")

# GraphML formatında kaydet (Gephi, Cytoscape vb. için)
nx.write_graphml(G, f"{output_dir}/nanocomposite_graph_basic.graphml")
print(f"✅ GraphML kaydedildi: {output_dir}/nanocomposite_graph_basic.graphml")

# JSON formatında kaydet
import json
from networkx.readwrite import json_graph

data = json_graph.node_link_data(G)
with open(f"{output_dir}/nanocomposite_graph.json", 'w') as f:
    json.dump(data, f, indent=2)
print(f"✅ JSON kaydedildi: {output_dir}/nanocomposite_graph.json")

# Basit metin raporu
print("\n📝 Graph analiz raporu oluşturuluyor...")

report = f"""
NANOCOMPOSITE GRAPH ANALİZİ
==========================

Graph İstatistikleri:
- Toplam düğüm sayısı: {G.number_of_nodes()}
- Toplam kenar sayısı: {G.number_of_edges()}
- Bağlantılı bileşen sayısı: {nx.number_connected_components(G)}

Düğüm Tipleri:
- Polimer sayısı: {len([n for n,d in G.nodes(data=True) if d.get('node_type')=='polymer'])}
- Modifikasyon sayısı: {len([n for n,d in G.nodes(data=True) if d.get('node_type')=='modification'])}
- Dispersiyon sayısı: {len([n for n,d in G.nodes(data=True) if d.get('node_type')=='dispersion'])}
- Polimer tipi sayısı: {len([n for n,d in G.nodes(data=True) if d.get('node_type')=='polymer_type'])}

En Çok Bağlantıya Sahip 10 Düğüm (Hub Nodes):
"""

# Degree centrality hesapla
degree_centrality = nx.degree_centrality(G)
top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

for i, (node, centrality) in enumerate(top_nodes, 1):
    degree = G.degree(node)
    report += f"\n{i}. {node} (bağlantı sayısı: {degree}, centrality: {centrality:.3f})"

# Raporu kaydet
with open(f"{output_dir}/graph_analysis_report.txt", 'w', encoding='utf-8') as f:
    f.write(report)

print(report)

print("\n✨ Tüm işlemler tamamlandı!")
print(f"📁 Oluşturulan dosyalar '{output_dir}' klasöründe:")
print("  - nanocomposite_graph_basic.graphml (Gephi/Cytoscape için)")
print("  - nanocomposite_graph.json (Programatik kullanım için)")
print("  - graph_analysis_report.txt (Analiz raporu)")

# PyVis ile interaktif HTML görselleştirme oluştur
try:
    from pyvis.network import Network
    
    print("\n🌐 İnteraktif HTML görselleştirme oluşturuluyor...")
    
    # PyVis network oluştur
    net = Network(height='800px', width='100%', notebook=False)
    
    # Düğümleri ekle
    for node, data in G.nodes(data=True):
        net.add_node(node, 
                    color=data.get('color', 'gray'),
                    size=data.get('size', 10),
                    title=f"{node} ({data.get('node_type', 'unknown')})")
    
    # Kenarları ekle
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target,
                    title=data.get('relation', ''),
                    color=data.get('color', 'gray'))
    
    # Fizik ayarları
    net.force_atlas_2based()
    net.show_buttons(filter_=['physics'])
    
    # HTML olarak kaydet
    net.save_graph(f"{output_dir}/nanocomposite_interactive_graph.html")
    print(f"✅ İnteraktif graph kaydedildi: {output_dir}/nanocomposite_interactive_graph.html")
    print("   (Bu dosyayı tarayıcıda açarak interaktif grafiği görebilirsiniz)")
    
except ImportError:
    print("\n⚠️ PyVis yüklü değil. İnteraktif görselleştirme için: pip install pyvis")