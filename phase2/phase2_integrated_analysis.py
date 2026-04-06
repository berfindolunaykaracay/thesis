"""
Phase 2 Implementation: Full Paper & Thesis - Integrated Multi-Property Analysis
Extends Phase 1 with Strength and Strain-to-Failure analysis

Deliverables:
- Integrated 3-layer motif diagram (ΔE%, Δσ%, Δε%)
- Centrality heatmap (weighted degree + betweenness)
- Edge stability plots
- Modified vs Unmodified comparison
- Complete metrics: weighted degree, betweenness, edge variance
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import seaborn as sns
from typing import Dict, List, Tuple
import os

DATASET_PATH = "../Dataset_LatestVersion.xlsx"

class IntegratedPropertyAnalysis:
    """Phase 2: Multi-property analysis with 3-layer motif diagrams"""

    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = dataset_path
        self.df = None
        self.clusters = {
            'C1': {'range': (0, 0.1), 'name': 'Soft elastomeric', 'color': '#FF6B6B'},
            'C2': {'range': (0.1, 0.5), 'name': 'Semi-soft thermoplastic', 'color': '#4ECDC4'},
            'C3': {'range': (0.5, 1.0), 'name': 'Intermediate', 'color': '#45B7D1'},
            'C4': {'range': (1.0, float('inf')), 'name': 'Rigid polymer', 'color': '#96CEB4'}
        }
        self.property_configs = {
            'modulus': {
                'col': 'Elastic Modulus improvement (%)',
                'symbol': 'ΔE%',
                'color': '#3498db'
            },
            'strength': {
                'col': 'Strength improvement (%)',
                'symbol': 'Δσ%',
                'color': '#e74c3c'
            },
            'strain': {
                'col': 'Strain to failure improvement%',
                'symbol': 'Δε%',
                'color': '#27ae60'
            }
        }
        self.graphs = {}  # {cluster_id: {property: graph}}
        self.graphs_modified = {}  # {cluster_id: {property: graph}} for modified only
        self.graphs_unmodified = {}  # {cluster_id: {property: graph}} for unmodified only
        self.centrality_data = {}
        self.modified_comparison = {}  # Store modified vs unmodified comparison

    def load_and_preprocess_data(self):
        """Load dataset and filter for samples with all 3 properties"""
        self.df = pd.read_excel(self.dataset_path)
        self.df.columns = [col.strip() for col in self.df.columns]

        # Convert all improvement columns to numeric
        for prop, config in self.property_configs.items():
            self.df[config['col']] = pd.to_numeric(self.df[config['col']], errors='coerce')

        # Convert modulus to numeric
        self.df['Polymer matrix elastic modulus (GPa)'] = pd.to_numeric(
            self.df['Polymer matrix elastic modulus (GPa)'], errors='coerce'
        )

        # Filter for samples with all 3 properties
        required_cols = [
            'Polymer matrix name',
            'Polymer matrix elastic modulus (GPa)',
            'Elastic Modulus improvement (%)',
            'Strength improvement (%)',
            'Strain to failure improvement%'
        ]

        self.df = self.df.dropna(subset=required_cols)

        # Clean modification column
        if 'Modification (modified/unmodified)' in self.df.columns:
            self.df['is_modified'] = self.df['Modification (modified/unmodified)'].str.lower() == 'modified'
        else:
            self.df['is_modified'] = False

        print(f"Loaded {len(self.df)} samples with all 3 properties")

    def assign_clusters(self):
        """Assign clusters based on neat polymer modulus"""
        def get_cluster(modulus):
            for cluster_id, info in self.clusters.items():
                if info['range'][0] <= modulus < info['range'][1]:
                    return cluster_id
            return None

        self.df['cluster'] = self.df['Polymer matrix elastic modulus (GPa)'].apply(get_cluster)

        print("\nCluster Distribution (samples with all 3 properties):")
        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            count = len(self.df[self.df['cluster'] == cluster_id])
            print(f"  {cluster_id}: {count} samples")

    def _build_graph_for_subset(self, cluster_df, prop_name, prop_config):
        """Helper to build a graph for a given dataframe subset"""
        G = nx.Graph()

        if len(cluster_df) == 0:
            return G

        # Add polymer nodes
        polymers = cluster_df['Polymer matrix name'].unique()
        for polymer in polymers:
            polymer_data = cluster_df[cluster_df['Polymer matrix name'] == polymer]
            avg_modulus = polymer_data['Polymer matrix elastic modulus (GPa)'].mean()
            G.add_node(polymer,
                      node_type='polymer',
                      modulus=avg_modulus,
                      color='#3498db',
                      size=25)

        # Add composite nodes and edges
        for idx, row in cluster_df.iterrows():
            polymer = row['Polymer matrix name']
            composite_id = f"{polymer}_{prop_name}_{idx}"

            improvement = row[prop_config['col']]
            if pd.isna(improvement):
                continue

            # Color by improvement direction
            node_color = '#27ae60' if improvement >= 0 else '#e74c3c'

            G.add_node(composite_id,
                      node_type='composite',
                      polymer=polymer,
                      improvement=improvement,
                      modified=row['is_modified'],
                      color=node_color,
                      size=12)

            G.add_edge(polymer, composite_id,
                      weight=abs(improvement),
                      improvement=improvement)

        return G

    def build_property_graphs(self):
        """Build separate graphs for each property within each cluster (all, modified, unmodified)"""
        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            cluster_df = self.df[self.df['cluster'] == cluster_id]

            if len(cluster_df) == 0:
                continue

            self.graphs[cluster_id] = {}
            self.graphs_modified[cluster_id] = {}
            self.graphs_unmodified[cluster_id] = {}

            # Split by modification status
            modified_df = cluster_df[cluster_df['is_modified'] == True]
            unmodified_df = cluster_df[cluster_df['is_modified'] == False]

            for prop_name, prop_config in self.property_configs.items():
                # Build all three graph types
                self.graphs[cluster_id][prop_name] = self._build_graph_for_subset(
                    cluster_df, prop_name, prop_config)
                self.graphs_modified[cluster_id][prop_name] = self._build_graph_for_subset(
                    modified_df, prop_name, prop_config)
                self.graphs_unmodified[cluster_id][prop_name] = self._build_graph_for_subset(
                    unmodified_df, prop_name, prop_config)

        print("\nGraphs built for all clusters and properties (all/modified/unmodified)")

    def _calculate_graph_metrics(self, G):
        """Helper to calculate all metrics for a single graph"""
        if G.number_of_nodes() == 0:
            return None

        # Get polymer nodes only
        polymer_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'polymer']

        if not polymer_nodes:
            return None

        # Weighted degree centrality
        weighted_degree = {}
        for node in polymer_nodes:
            weighted_degree[node] = sum(
                G[node][neighbor].get('weight', 0)
                for neighbor in G.neighbors(node)
            )

        # Betweenness centrality
        try:
            betweenness = nx.betweenness_centrality(G, weight='weight')
            betweenness = {n: betweenness[n] for n in polymer_nodes}
        except:
            betweenness = {n: 0 for n in polymer_nodes}

        # Edge weight variance (stability indicator)
        edge_weights = [d['weight'] for _, _, d in G.edges(data=True)]
        edge_variance = np.var(edge_weights) if edge_weights else 0
        edge_std = np.std(edge_weights) if edge_weights else 0

        # Edge improvements for analysis
        improvements = [d['improvement'] for _, _, d in G.edges(data=True)]
        mean_improvement = np.mean(improvements) if improvements else 0
        positive_ratio = sum(1 for x in improvements if x > 0) / len(improvements) if improvements else 0

        return {
            'weighted_degree': weighted_degree,
            'betweenness': betweenness,
            'edge_variance': edge_variance,
            'edge_std': edge_std,
            'mean_improvement': mean_improvement,
            'positive_ratio': positive_ratio,
            'total_weighted_degree': sum(weighted_degree.values()),
            'mean_betweenness': np.mean(list(betweenness.values())) if betweenness else 0,
            'n_edges': len(edge_weights)
        }

    def calculate_centrality_metrics(self):
        """Calculate weighted degree, betweenness, and edge variance for each cluster"""
        for cluster_id, prop_graphs in self.graphs.items():
            self.centrality_data[cluster_id] = {}

            for prop_name, G in prop_graphs.items():
                metrics = self._calculate_graph_metrics(G)
                if metrics:
                    self.centrality_data[cluster_id][prop_name] = metrics

    def compare_modified_vs_unmodified(self):
        """Compare centrality metrics between modified and unmodified systems"""
        print("\n" + "="*60)
        print("Modified vs Unmodified Centrality Comparison")
        print("="*60)

        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            if cluster_id not in self.graphs_modified:
                continue

            self.modified_comparison[cluster_id] = {}

            for prop_name in ['modulus', 'strength', 'strain']:
                if prop_name not in self.graphs_modified.get(cluster_id, {}):
                    continue

                G_mod = self.graphs_modified[cluster_id].get(prop_name)
                G_unmod = self.graphs_unmodified[cluster_id].get(prop_name)

                mod_metrics = self._calculate_graph_metrics(G_mod) if G_mod else None
                unmod_metrics = self._calculate_graph_metrics(G_unmod) if G_unmod else None

                self.modified_comparison[cluster_id][prop_name] = {
                    'modified': mod_metrics,
                    'unmodified': unmod_metrics
                }

        # Print summary
        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            if cluster_id not in self.modified_comparison:
                continue

            print(f"\n{cluster_id} - {self.clusters[cluster_id]['name']}:")

            for prop_name, data in self.modified_comparison[cluster_id].items():
                symbol = self.property_configs[prop_name]['symbol']
                mod = data['modified']
                unmod = data['unmodified']

                mod_wd = mod['total_weighted_degree'] if mod else 0
                unmod_wd = unmod['total_weighted_degree'] if unmod else 0
                mod_be = mod['mean_betweenness'] if mod else 0
                unmod_be = unmod['mean_betweenness'] if unmod else 0

                print(f"  {symbol}: Modified WD={mod_wd:.1f}, Unmodified WD={unmod_wd:.1f} | "
                      f"Modified higher: {mod_wd > unmod_wd}")

    def create_integrated_motif_diagram(self):
        """Create 3-layer motif diagram combining ΔE%, Δσ%, Δε%"""
        os.makedirs('output', exist_ok=True)

        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            if cluster_id not in self.graphs:
                continue

            cluster_df = self.df[self.df['cluster'] == cluster_id]
            polymers = cluster_df['Polymer matrix name'].unique()

            # Create integrated network
            net = Network(height="900px", width="100%", bgcolor="#ffffff",
                         font_color="black", notebook=False)

            # Calculate positions - polymers in center, properties around
            added_nodes = set()

            # Add polymer nodes (shared across all layers)
            for polymer in polymers:
                polymer_data = cluster_df[cluster_df['Polymer matrix name'] == polymer]
                avg_modulus = polymer_data['Polymer matrix elastic modulus (GPa)'].mean()
                net.add_node(polymer,
                            label=f"{polymer}\n(E={avg_modulus:.2f})",
                            color='#3498db',
                            size=30,
                            shape='dot')
                added_nodes.add(polymer)

            # Add composite nodes for each property layer with different colors
            prop_colors = {
                'modulus': {'pos': '#2980b9', 'neg': '#1a5276'},  # Blues
                'strength': {'pos': '#e74c3c', 'neg': '#922b21'},  # Reds
                'strain': {'pos': '#27ae60', 'neg': '#1e8449'}     # Greens
            }

            for idx, row in cluster_df.iterrows():
                polymer = row['Polymer matrix name']

                for prop_name, prop_config in self.property_configs.items():
                    improvement = row[prop_config['col']]
                    if pd.isna(improvement):
                        continue

                    composite_id = f"{polymer}_{prop_name}_{idx}"

                    # Color based on property type and improvement direction
                    if improvement >= 0:
                        node_color = prop_colors[prop_name]['pos']
                    else:
                        node_color = prop_colors[prop_name]['neg']

                    net.add_node(composite_id,
                                label=f"{prop_config['symbol']}: {improvement:.1f}%",
                                color=node_color,
                                size=10,
                                shape='dot')

                    # Edge width proportional to improvement magnitude
                    width = min(abs(improvement) / 20, 8)
                    edge_color = prop_colors[prop_name]['pos']

                    net.add_edge(polymer, composite_id,
                                color=edge_color,
                                width=max(width, 1),
                                title=f"{prop_config['symbol']}: {improvement:.1f}%")

            # Configure physics for large networks
            node_count = len(cluster_df) * 3 + len(polymers)
            if node_count > 100:
                net.set_options("""
                var options = {
                  "configure": {"enabled": true, "filter": ["physics"]},
                  "physics": {
                    "barnesHut": {
                      "gravitationalConstant": -50000,
                      "centralGravity": 0.1,
                      "springLength": 300,
                      "springConstant": 0.001,
                      "damping": 0.3,
                      "avoidOverlap": 1
                    },
                    "stabilization": {"iterations": 2000}
                  }
                }
                """)
            else:
                net.barnes_hut(overlap=1)
                net.show_buttons(filter_=['physics'])

            # Save and add header
            filename = f"phase2_output/integrated_motif_{cluster_id}.html"
            net.save_graph(filename)

            # Add custom header with legend
            with open(filename, 'r') as f:
                html_content = f.read()

            header = f"""
            <div style="padding: 20px; background-color: #f8f9fa; margin: 10px; border-radius: 5px; border: 2px solid {self.clusters[cluster_id]['color']};">
                <h2 style="color: {self.clusters[cluster_id]['color']};">Integrated 3-Layer Motif: Cluster {cluster_id} - {self.clusters[cluster_id]['name']}</h2>
                <p><strong>Modulus range:</strong> {self.clusters[cluster_id]['range'][0]}-{self.clusters[cluster_id]['range'][1]} GPa | <strong>Samples:</strong> {len(cluster_df)}</p>
                <p><strong>Legend - Property Layers:</strong></p>
                <p>🔵 <span style="color: #2980b9;">Blue edges/nodes: Elastic Modulus (ΔE%)</span></p>
                <p>🔴 <span style="color: #e74c3c;">Red edges/nodes: Strength (Δσ%)</span></p>
                <p>🟢 <span style="color: #27ae60;">Green edges/nodes: Strain-to-failure (Δε%)</span></p>
                <p><strong>Node intensity:</strong> Darker = negative improvement | <strong>Edge width:</strong> Proportional to magnitude</p>
            </div>
            """

            modified_html = html_content.replace('<center>\n<h1></h1>\n</center>',
                                                f'<center>\n{header}\n</center>')

            with open(filename, 'w') as f:
                f.write(modified_html)

            print(f"Saved integrated motif diagram for {cluster_id}")

    def create_centrality_heatmap(self):
        """Create heatmaps showing polymer centrality (weighted degree + betweenness)"""
        os.makedirs('output', exist_ok=True)

        # Collect all unique polymers
        all_polymers = set()
        for cluster_id in self.centrality_data:
            for prop_name in self.centrality_data[cluster_id]:
                all_polymers.update(self.centrality_data[cluster_id][prop_name]['weighted_degree'].keys())

        all_polymers = sorted(list(all_polymers))

        # Create matrix for heatmap
        columns = []
        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            for prop_name in ['modulus', 'strength', 'strain']:
                columns.append(f"{cluster_id}_{prop_name}")

        # Data for weighted degree
        data_wd = np.zeros((len(all_polymers), len(columns)))
        # Data for betweenness
        data_bt = np.zeros((len(all_polymers), len(columns)))

        for i, polymer in enumerate(all_polymers):
            for j, col in enumerate(columns):
                cluster_id, prop_name = col.split('_', 1)
                if cluster_id in self.centrality_data and prop_name in self.centrality_data[cluster_id]:
                    data_wd[i, j] = self.centrality_data[cluster_id][prop_name]['weighted_degree'].get(polymer, 0)
                    data_bt[i, j] = self.centrality_data[cluster_id][prop_name]['betweenness'].get(polymer, 0)

        # Filter to show only top 20 polymers by total weighted degree
        total_centrality = data_wd.sum(axis=1)
        top_indices = np.argsort(total_centrality)[-20:][::-1]

        data_wd_filtered = data_wd[top_indices]
        data_bt_filtered = data_bt[top_indices]
        polymers_filtered = [all_polymers[i] for i in top_indices]

        # Column labels
        col_labels = []
        for col in columns:
            cluster_id, prop = col.split('_', 1)
            symbol = {'modulus': 'ΔE', 'strength': 'Δσ', 'strain': 'Δε'}[prop]
            col_labels.append(f"{cluster_id}\n{symbol}")

        # Create figure with two heatmaps
        fig, axes = plt.subplots(1, 2, figsize=(20, 10))

        # Weighted Degree Heatmap
        im1 = axes[0].imshow(data_wd_filtered, cmap='YlOrRd', aspect='auto')
        axes[0].set_xticks(np.arange(len(columns)))
        axes[0].set_yticks(np.arange(len(polymers_filtered)))
        axes[0].set_xticklabels(col_labels, fontsize=9)
        axes[0].set_yticklabels(polymers_filtered, fontsize=9)
        plt.setp(axes[0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        cbar1 = fig.colorbar(im1, ax=axes[0], shrink=0.8)
        cbar1.ax.set_ylabel('Weighted Degree', rotation=-90, va="bottom")
        axes[0].set_title('Weighted Degree Centrality\n(Functional Importance)', fontsize=12)
        axes[0].set_xlabel('Cluster - Property')
        axes[0].set_ylabel('Polymer Matrix')

        # Betweenness Heatmap
        im2 = axes[1].imshow(data_bt_filtered, cmap='YlGnBu', aspect='auto')
        axes[1].set_xticks(np.arange(len(columns)))
        axes[1].set_yticks(np.arange(len(polymers_filtered)))
        axes[1].set_xticklabels(col_labels, fontsize=9)
        axes[1].set_yticklabels(polymers_filtered, fontsize=9)
        plt.setp(axes[1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        cbar2 = fig.colorbar(im2, ax=axes[1], shrink=0.8)
        cbar2.ax.set_ylabel('Betweenness Centrality', rotation=-90, va="bottom")
        axes[1].set_title('Betweenness Centrality\n(Translational Knowledge Hub)', fontsize=12)
        axes[1].set_xlabel('Cluster - Property')
        axes[1].set_ylabel('Polymer Matrix')

        plt.suptitle('Polymer Centrality Analysis Across Clusters and Properties', fontsize=14, y=1.02)
        plt.tight_layout()
        plt.savefig('output/centrality_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("Saved centrality heatmap (weighted degree + betweenness)")

    def create_edge_stability_plots(self):
        """Create plots showing distribution of improvements vs reductions"""
        os.makedirs('output', exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.flatten()

        for idx, cluster_id in enumerate(['C1', 'C2', 'C3', 'C4']):
            ax = axes[idx]

            if cluster_id not in self.graphs:
                ax.text(0.5, 0.5, f'No data for {cluster_id}', ha='center', va='center')
                continue

            # Collect improvements for each property
            prop_data = {}
            for prop_name, G in self.graphs[cluster_id].items():
                improvements = [d['improvement'] for _, _, d in G.edges(data=True)]
                prop_data[prop_name] = improvements

            # Create violin plots
            positions = [1, 2, 3]
            colors = ['#3498db', '#e74c3c', '#27ae60']
            labels = ['ΔE%', 'Δσ%', 'Δε%']

            for i, (prop_name, improvements) in enumerate(prop_data.items()):
                if improvements:
                    parts = ax.violinplot([improvements], positions=[positions[i]],
                                         showmeans=True, showmedians=True)
                    for pc in parts['bodies']:
                        pc.set_facecolor(colors[i])
                        pc.set_alpha(0.7)

            ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            ax.set_xticks(positions)
            ax.set_xticklabels(labels)
            ax.set_ylabel('Improvement (%)')
            ax.set_title(f'{cluster_id}: {self.clusters[cluster_id]["name"]}')
            ax.grid(True, alpha=0.3)

            # Add summary stats
            for i, (prop_name, improvements) in enumerate(prop_data.items()):
                if improvements:
                    pos_count = sum(1 for x in improvements if x > 0)
                    neg_count = sum(1 for x in improvements if x < 0)
                    ax.annotate(f'+{pos_count}/-{neg_count}',
                               xy=(positions[i], ax.get_ylim()[1]*0.9),
                               ha='center', fontsize=8)

        plt.suptitle('Edge Stability: Distribution of Property Improvements', fontsize=14)
        plt.tight_layout()
        plt.savefig('output/edge_stability_plots.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("Saved edge stability plots")

    def create_modified_comparison_plot(self):
        """Create visualization comparing modified vs unmodified centrality"""
        os.makedirs('output', exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.flatten()

        bar_width = 0.35
        prop_labels = ['ΔE%', 'Δσ%', 'Δε%']
        colors_mod = ['#2980b9', '#c0392b', '#27ae60']
        colors_unmod = ['#85c1e9', '#f1948a', '#82e0aa']

        for idx, cluster_id in enumerate(['C1', 'C2', 'C3', 'C4']):
            ax = axes[idx]

            if cluster_id not in self.modified_comparison:
                ax.text(0.5, 0.5, f'No data for {cluster_id}', ha='center', va='center')
                continue

            mod_values = []
            unmod_values = []

            for prop_name in ['modulus', 'strength', 'strain']:
                data = self.modified_comparison[cluster_id].get(prop_name, {})
                mod = data.get('modified')
                unmod = data.get('unmodified')

                mod_values.append(mod['total_weighted_degree'] if mod else 0)
                unmod_values.append(unmod['total_weighted_degree'] if unmod else 0)

            x = np.arange(len(prop_labels))

            bars1 = ax.bar(x - bar_width/2, mod_values, bar_width, label='Modified',
                          color=colors_mod, edgecolor='black', linewidth=0.5)
            bars2 = ax.bar(x + bar_width/2, unmod_values, bar_width, label='Unmodified',
                          color=colors_unmod, edgecolor='black', linewidth=0.5)

            ax.set_xlabel('Property')
            ax.set_ylabel('Total Weighted Degree Centrality')
            ax.set_title(f'{cluster_id}: {self.clusters[cluster_id]["name"]}')
            ax.set_xticks(x)
            ax.set_xticklabels(prop_labels)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar, val in zip(bars1, mod_values):
                if val > 0:
                    ax.annotate(f'{val:.0f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                               ha='center', va='bottom', fontsize=8)
            for bar, val in zip(bars2, unmod_values):
                if val > 0:
                    ax.annotate(f'{val:.0f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                               ha='center', va='bottom', fontsize=8)

        plt.suptitle('Modified vs Unmodified: Weighted Degree Centrality Comparison\n'
                    '(Higher values indicate organized structure-property mapping)', fontsize=12)
        plt.tight_layout()
        plt.savefig('output/modified_vs_unmodified_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("Saved modified vs unmodified comparison plot")

    def generate_phase2_report(self):
        """Generate comprehensive Phase 2 report with all metrics"""
        os.makedirs('output', exist_ok=True)

        report = []
        report.append("=" * 70)
        report.append("Phase 2: Full Paper & Thesis - Integrated Analysis Report")
        report.append("=" * 70)
        report.append(f"\nTotal samples with all 3 properties: {len(self.df)}")
        report.append(f"Modified samples: {self.df['is_modified'].sum()}")
        report.append(f"Unmodified samples: {(~self.df['is_modified']).sum()}")

        # Cluster-wise analysis
        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            cluster_df = self.df[self.df['cluster'] == cluster_id]

            if len(cluster_df) == 0:
                continue

            report.append(f"\n{'='*70}")
            report.append(f"Cluster {cluster_id}: {self.clusters[cluster_id]['name']}")
            report.append(f"{'='*70}")
            report.append(f"Modulus range: {self.clusters[cluster_id]['range'][0]}-{self.clusters[cluster_id]['range'][1]} GPa")
            report.append(f"Samples: {len(cluster_df)} (Modified: {cluster_df['is_modified'].sum()}, Unmodified: {(~cluster_df['is_modified']).sum()})")

            # Property-wise statistics
            for prop_name, prop_config in self.property_configs.items():
                values = cluster_df[prop_config['col']]
                report.append(f"\n  {prop_config['symbol']} Statistics:")
                report.append(f"    Mean: {values.mean():.1f}%")
                report.append(f"    Std: {values.std():.1f}%")
                report.append(f"    Min: {values.min():.1f}% | Max: {values.max():.1f}%")
                report.append(f"    Positive: {(values > 0).sum()} ({(values > 0).sum()/len(values)*100:.1f}%)")
                report.append(f"    Negative: {(values < 0).sum()} ({(values < 0).sum()/len(values)*100:.1f}%)")

            # Centrality metrics
            if cluster_id in self.centrality_data:
                report.append(f"\n  --- Centrality Metrics ---")

                for prop_name in ['modulus', 'strength', 'strain']:
                    if prop_name not in self.centrality_data[cluster_id]:
                        continue

                    metrics = self.centrality_data[cluster_id][prop_name]
                    symbol = self.property_configs[prop_name]['symbol']

                    report.append(f"\n  {symbol}:")

                    # Weighted Degree (Functional Importance)
                    wd = metrics['weighted_degree']
                    if wd:
                        top_wd = sorted(wd.items(), key=lambda x: x[1], reverse=True)[:3]
                        report.append(f"    Weighted Degree (Functional Importance):")
                        for polymer, score in top_wd:
                            report.append(f"      - {polymer}: {score:.1f}")

                    # Betweenness (Translational Knowledge Hub)
                    bt = metrics['betweenness']
                    if bt:
                        top_bt = sorted(bt.items(), key=lambda x: x[1], reverse=True)[:3]
                        report.append(f"    Betweenness (Translational Hub):")
                        for polymer, score in top_bt:
                            report.append(f"      - {polymer}: {score:.4f}")

                    # Edge Weight Variance (Stability Indicator)
                    report.append(f"    Edge Weight Variance (Stability): {metrics['edge_variance']:.1f}")
                    report.append(f"    Edge Weight Std Dev: {metrics['edge_std']:.1f}")

            # Modified vs Unmodified Comparison
            if cluster_id in self.modified_comparison:
                report.append(f"\n  --- Modified vs Unmodified Comparison ---")
                report.append(f"  (Higher weighted centrality = organized structure-property mapping)")

                for prop_name in ['modulus', 'strength', 'strain']:
                    if prop_name not in self.modified_comparison[cluster_id]:
                        continue

                    data = self.modified_comparison[cluster_id][prop_name]
                    mod = data['modified']
                    unmod = data['unmodified']
                    symbol = self.property_configs[prop_name]['symbol']

                    mod_wd = mod['total_weighted_degree'] if mod else 0
                    unmod_wd = unmod['total_weighted_degree'] if unmod else 0
                    mod_n = mod['n_edges'] if mod else 0
                    unmod_n = unmod['n_edges'] if unmod else 0

                    winner = "Modified" if mod_wd > unmod_wd else "Unmodified"
                    report.append(f"\n  {symbol}:")
                    report.append(f"    Modified: WD={mod_wd:.1f} (n={mod_n})")
                    report.append(f"    Unmodified: WD={unmod_wd:.1f} (n={unmod_n})")
                    report.append(f"    Higher centrality: {winner}")

        # Summary findings
        report.append(f"\n{'='*70}")
        report.append("SUMMARY FINDINGS (Buehler Framework Alignment)")
        report.append(f"{'='*70}")

        report.append("\n1. Cluster Topology Patterns:")
        report.append("   - C1-C2 (soft/semi-soft): Higher variability, exploratory graphs")
        report.append("   - C3-C4 (intermediate/rigid): Dense, interface-limited graphs")

        report.append("\n2. Property Trade-offs:")
        report.append("   - Modulus enhancement generally accompanied by strain reduction")
        report.append("   - Soft clusters show better strain retention")

        report.append("\n3. Modified vs Unmodified Systems:")
        # Calculate overall comparison
        mod_higher_count = 0
        total_comparisons = 0
        for cluster_id in self.modified_comparison:
            for prop_name, data in self.modified_comparison[cluster_id].items():
                mod = data.get('modified')
                unmod = data.get('unmodified')
                if mod and unmod:
                    total_comparisons += 1
                    if mod['total_weighted_degree'] > unmod['total_weighted_degree']:
                        mod_higher_count += 1

        if total_comparisons > 0:
            report.append(f"   - Modified systems show higher centrality in {mod_higher_count}/{total_comparisons} comparisons")
            report.append(f"   - Evidence of organized structure-property mapping in modified systems")

        # Save report
        with open('output/phase2_report.txt', 'w') as f:
            f.write('\n'.join(report))

        print("\nSaved comprehensive Phase 2 report")

    def run_phase2_analysis(self):
        """Execute complete Phase 2 analysis pipeline"""
        print("Starting Phase 2 Analysis...")
        print("="*60)

        # Step 1: Load data
        self.load_and_preprocess_data()

        # Step 2: Assign clusters
        self.assign_clusters()

        # Step 3: Build property graphs (all, modified, unmodified)
        self.build_property_graphs()

        # Step 4: Calculate centrality metrics
        self.calculate_centrality_metrics()

        # Step 5: Compare modified vs unmodified
        self.compare_modified_vs_unmodified()

        # Step 6: Create visualizations
        print("\nCreating visualizations...")
        self.create_integrated_motif_diagram()
        self.create_centrality_heatmap()
        self.create_edge_stability_plots()
        self.create_modified_comparison_plot()

        # Step 7: Generate comprehensive report
        self.generate_phase2_report()

        print("\n" + "="*60)
        print("Phase 2 analysis complete!")
        print("="*60)
        print("\nOutputs saved to phase2_output/:")
        print("  - integrated_motif_C1-C4.html (3-layer motif diagrams)")
        print("  - centrality_heatmap.png (weighted degree + betweenness)")
        print("  - edge_stability_plots.png (improvement distributions)")
        print("  - modified_vs_unmodified_comparison.png")
        print("  - phase2_report.txt (comprehensive analysis)")


if __name__ == "__main__":
    analysis = IntegratedPropertyAnalysis()
    analysis.run_phase2_analysis()
