#!/usr/bin/env python3
# Test - Basit graph yükleme kontrolü

from pyvis.network import Network

# Basit test graph
net = Network(height='600px', width='100%', bgcolor='#222222', font_color='white')

# Test node'ları
net.add_node(1, label="Test 1", color='blue')
net.add_node(2, label="Test 2", color='red')

# Test edge
net.add_edge(1, 2, label="0.5", width=2, color='gray')

# Kaydet
net.save_graph('test_graph.html')
print("Test graph oluşturuldu: test_graph.html")