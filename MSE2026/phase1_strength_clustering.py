"""
Phase 1 Implementation: Conference Stage - Strength Clustering and Analysis
This implements the strength-based clustering approach for polymer-MMT nanocomposites
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import seaborn as sns
from typing import Dict, List, Tuple
import os

# Dataset configuration
DATASET_PATH = "../Dataset_LatestVersion.xlsx"

class StrengthClusteringAnalysis:
    """Implements Phase 1: Strength-based clustering and graph analysis"""

    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = dataset_path
        self.df = None
        self.clusters = {
            'C1': {'range': (0, 10), 'name': 'Low strength', 'color': '#FF6B6B'},
            'C2': {'range': (10, 30), 'name': 'Medium-low strength', 'color': '#4ECDC4'},
            'C3': {'range': (30, 60), 'name': 'Medium strength', 'color': '#45B7D1'},
            'C4': {'range': (60, float('inf')), 'name': 'High strength', 'color': '#96CEB4'}
        }
        self.graphs = {}
        self.centrality_metrics = {}

    def load_and_preprocess_data(self):
        """Load dataset and preprocess for clustering analysis"""
        self.df = pd.read_excel(self.dataset_path)

        # Clean column names
        self.df.columns = [col.strip() for col in self.df.columns]

        # Print all column names to help identify correct ones
        print("Available columns:")
        for col in self.df.columns:
            if 'strength' in col.lower() or 'Strength' in col:
                print(f"  - {col}")

        # Essential columns for Phase 1 (Strength-based)
        required_cols = [
            'Polymer matrix name',
            'Polymer matrix Strength (MPa)',
            'Nanocomposite Strength (MPa)',
            'Strength improvement (%)',
            'Modification (modified/unmodified)'
        ]

        # Check if columns exist
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols}")

        # Drop rows with missing data in ANY required column (keep only complete data)
        print(f"Total rows before cleaning: {len(self.df)}")
        self.df = self.df.dropna(subset=required_cols)
        print(f"Rows with complete data: {len(self.df)}")

        # Convert strength to float
        self.df['Polymer matrix Strength (MPa)'] = pd.to_numeric(
            self.df['Polymer matrix Strength (MPa)'], errors='coerce'
        )

        # Convert improvement percentages to numeric
        self.df['Strength improvement (%)'] = pd.to_numeric(
            self.df['Strength improvement (%)'], errors='coerce'
        )

        # Clean modification column
        self.df['is_modified'] = self.df['Modification (modified/unmodified)'].str.lower() == 'modified'

        print(f"Loaded {len(self.df)} samples after preprocessing")

    def assign_clusters(self):
        """Assign each polymer to a cluster based on neat polymer strength"""
        def get_cluster(strength):
            for cluster_id, cluster_info in self.clusters.items():
                if cluster_info['range'][0] <= strength < cluster_info['range'][1]:
                    return cluster_id
            return None

        self.df['cluster'] = self.df['Polymer matrix Strength (MPa)'].apply(get_cluster)

        # Print cluster distribution
        print("\nCluster Distribution:")
        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            count = len(self.df[self.df['cluster'] == cluster_id])
            print(f"{cluster_id} ({self.clusters[cluster_id]['name']}): {count} samples")

    def build_cluster_graphs(self):
        """Build graphs for each cluster"""
        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            cluster_df = self.df[self.df['cluster'] == cluster_id]

            if len(cluster_df) == 0:
                print(f"No samples in cluster {cluster_id}")
                continue

            # Create graph for this cluster
            G = nx.Graph()

            # Add nodes and edges based on polymer relationships
            polymers = cluster_df['Polymer matrix name'].unique()

            # Add polymer nodes (blue) - larger size for visibility
            for polymer in polymers:
                polymer_data = cluster_df[cluster_df['Polymer matrix name'] == polymer]
                avg_matrix_strength = polymer_data['Polymer matrix Strength (MPa)'].mean()
                G.add_node(polymer,
                          node_type='polymer',
                          strength=avg_matrix_strength,
                          color='#3498db',
                          size=35)

            # Add composite nodes and edges
            for idx, row in cluster_df.iterrows():
                polymer = row['Polymer matrix name']

                # Create unique composite node ID
                composite_id = f"{polymer}_composite_{idx}"

                # Get improvement value
                improvement = row.get('Strength improvement (%)', 0)
                if pd.notna(improvement):
                    improvement = float(improvement)
                else:
                    improvement = 0

                # Determine node color based on improvement (as per document)
                # Green/red nodes: composites - colored by improvement
                if improvement >= 0:
                    node_color = '#27ae60'  # Green for positive improvement
                else:
                    node_color = '#e74c3c'  # Red for negative improvement

                # Add composite node - larger size for visibility
                if pd.notna(row.get('Nanocomposite Strength (MPa)')):
                    G.add_node(composite_id,
                              node_type='composite',
                              polymer=polymer,
                              strength=row['Nanocomposite Strength (MPa)'],
                              improvement=improvement,
                              modified=row['is_modified'],
                              color=node_color,
                              size=25)

                    # Add edge with weight based on improvement
                    # Edge weight is absolute improvement percentage
                    weight = abs(improvement)
                    G.add_edge(polymer, composite_id,
                              weight=weight,
                              improvement=improvement)

            self.graphs[cluster_id] = G
            print(f"\nCluster {cluster_id}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    def calculate_centrality_metrics(self):
        """Calculate centrality metrics for each cluster"""
        for cluster_id, G in self.graphs.items():
            if G.number_of_nodes() == 0:
                continue

            metrics = {}

            # Degree centrality
            degree_cent = nx.degree_centrality(G)

            # Weighted degree (sum of edge weights)
            weighted_degree = {}
            for node in G.nodes():
                weighted_degree[node] = sum(G[node][neighbor].get('weight', 0)
                                          for neighbor in G.neighbors(node))

            # Betweenness centrality
            betweenness_cent = nx.betweenness_centrality(G, weight='weight')

            # Filter for polymer nodes only
            polymer_nodes = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'polymer']

            metrics['degree'] = {n: degree_cent[n] for n in polymer_nodes}
            metrics['weighted_degree'] = {n: weighted_degree[n] for n in polymer_nodes}
            metrics['betweenness'] = {n: betweenness_cent[n] for n in polymer_nodes}

            self.centrality_metrics[cluster_id] = metrics

            # Print top polymers by centrality
            print(f"\nCluster {cluster_id} - Top 3 polymers by weighted degree:")
            sorted_polymers = sorted(metrics['weighted_degree'].items(),
                                   key=lambda x: x[1], reverse=True)[:3]
            for polymer, score in sorted_polymers:
                print(f"  {polymer}: {score:.2f}")

    def compare_modified_vs_unmodified(self):
        """Compare centrality metrics between modified and unmodified systems"""
        results = {}

        for cluster_id, G in self.graphs.items():
            if G.number_of_nodes() == 0:
                continue

            # Separate modified and unmodified composite nodes
            modified_nodes = [n for n in G.nodes()
                            if G.nodes[n].get('node_type') == 'composite'
                            and G.nodes[n].get('modified')]
            unmodified_nodes = [n for n in G.nodes()
                              if G.nodes[n].get('node_type') == 'composite'
                              and not G.nodes[n].get('modified')]

            # Calculate average improvements
            mod_improvements = []
            unmod_improvements = []

            for edge in G.edges(data=True):
                if edge[1] in modified_nodes:
                    mod_improvements.append(edge[2].get('improvement', 0))
                elif edge[1] in unmodified_nodes:
                    unmod_improvements.append(edge[2].get('improvement', 0))

            results[cluster_id] = {
                'modified_count': len(modified_nodes),
                'unmodified_count': len(unmodified_nodes),
                'avg_mod_improvement': np.mean(mod_improvements) if mod_improvements else 0,
                'avg_unmod_improvement': np.mean(unmod_improvements) if unmod_improvements else 0
            }

        return results

    def visualize_cluster_graphs(self):
        """Create interactive visualizations for each cluster"""
        os.makedirs('output', exist_ok=True)

        for cluster_id, G in self.graphs.items():
            if G.number_of_nodes() == 0:
                continue

            # Create PyVis network
            net = Network(height="800px", width="100%", bgcolor="#ffffff",
                         font_color="black", notebook=False)

            # Configure physics based on cluster size
            node_count = G.number_of_nodes()
            if node_count > 200:  # Large clusters
                net.set_options("""
                var options = {
                  "configure": {
                    "enabled": true,
                    "filter": ["physics"]
                  },
                  "physics": {
                    "enabled": true,
                    "barnesHut": {
                      "gravitationalConstant": -80000,
                      "centralGravity": 0.01,
                      "springLength": 500,
                      "springConstant": 0.001,
                      "damping": 0.5,
                      "avoidOverlap": 1
                    },
                    "stabilization": {"iterations": 3000}
                  }
                }
                """)
            else:  # Smaller clusters
                net.barnes_hut(overlap=1)
                # Add physics control panel
                net.show_buttons(filter_=['physics'])

            # Add nodes
            for node, attrs in G.nodes(data=True):
                label = node
                if attrs['node_type'] == 'polymer':
                    label = f"{node}\n(σ={attrs['strength']:.2f} MPa)"
                net.add_node(node, label=label, color=attrs['color'], size=attrs['size'])

            # Add edges - weighted by improvement magnitude
            for source, target, attrs in G.edges(data=True):
                # Minimum width 2, scaled up to max 15 for better visibility
                width = max(2, min(attrs['weight'] / 5, 15))  # Scale edge width by improvement %
                title = f"Improvement: {attrs.get('improvement', 0):.1f}%"
                net.add_edge(source, target, color='gray', width=width, title=title)

            # Add cluster info to visualization
            cluster_df = self.df[self.df['cluster'] == cluster_id]
            n_samples = len(cluster_df)
            avg_improvement = cluster_df['Strength improvement (%)'].mean()
            pct_modified = (cluster_df['is_modified'].sum() / n_samples) * 100

            # Save basic visualization
            filename = f"output/cluster_{cluster_id}_graph.html"
            net.save_graph(filename)

            # Post-process HTML to add cluster information
            with open(filename, 'r') as f:
                html_content = f.read()

            # Add cluster information header
            cluster_info = f"""
            <div style="padding: 20px; background-color: #f8f9fa; margin: 10px; border-radius: 5px; border: 2px solid {self.clusters[cluster_id]['color']};">
                <h2 style="color: {self.clusters[cluster_id]['color']};">Cluster {cluster_id}: {self.clusters[cluster_id]['name']}</h2>
                <p><strong>Strength range:</strong> {self.clusters[cluster_id]['range'][0]}-{self.clusters[cluster_id]['range'][1]} MPa</p>
                <p><strong>n_samples:</strong> {n_samples} | <strong>avg Δσ%:</strong> {avg_improvement:.1f}% | <strong>% modified:</strong> {pct_modified:.1f}%</p>
                <p><strong>Legend:</strong> 🔵 Blue: Polymer matrices | 🟢 Green: Positive improvement | 🔴 Red: Negative improvement</p>
                <p><strong>Edge width:</strong> Proportional to improvement magnitude (%)</p>
            </div>
            """

            # Insert cluster info after the first <center> tag
            modified_html = html_content.replace('<center>\n<h1></h1>\n</center>',
                                                f'<center>\n{cluster_info}\n</center>')

            # Write back the modified HTML
            with open(filename, 'w') as f:
                f.write(modified_html)

            print(f"Saved visualization for cluster {cluster_id}")

    def generate_summary_report(self):
        """Generate summary report for conference paper"""
        report = []
        report.append("=== Phase 1: Conference Stage Analysis ===\n")
        report.append("Strength-Based Clustering Results\n")

        # Overall statistics
        report.append(f"Total samples: {len(self.df)}")
        report.append(f"Modified samples: {self.df['is_modified'].sum()}")
        report.append(f"Unmodified samples: {(~self.df['is_modified']).sum()}\n")

        # Cluster-wise analysis
        comparison = self.compare_modified_vs_unmodified()

        for cluster_id in ['C1', 'C2', 'C3', 'C4']:
            report.append(f"\n{cluster_id} - {self.clusters[cluster_id]['name']} regime:")
            report.append(f"  Range: {self.clusters[cluster_id]['range'][0]}-{self.clusters[cluster_id]['range'][1]} MPa")

            if cluster_id in comparison:
                comp = comparison[cluster_id]
                report.append(f"  Modified: {comp['modified_count']} samples, avg improvement: {comp['avg_mod_improvement']:.1f}%")
                report.append(f"  Unmodified: {comp['unmodified_count']} samples, avg improvement: {comp['avg_unmod_improvement']:.1f}%")

            if cluster_id in self.centrality_metrics:
                metrics = self.centrality_metrics[cluster_id]
                top_polymer = max(metrics['weighted_degree'].items(), key=lambda x: x[1])[0]
                report.append(f"  Knowledge hub: {top_polymer}")

        # Save report
        with open('output/conference_summary.txt', 'w') as f:
            f.write('\n'.join(report))

        print("\nSummary report saved to output/conference_summary.txt")

    def create_summary_figure(self):
        """Create summary figure showing all four clusters"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()

        for idx, cluster_id in enumerate(['C1', 'C2', 'C3', 'C4']):
            ax = axes[idx]
            cluster_df = self.df[self.df['cluster'] == cluster_id]

            if len(cluster_df) == 0:
                ax.text(0.5, 0.5, f'No data for {cluster_id}',
                       ha='center', va='center', transform=ax.transAxes)
                continue

            # Scatter plot: Matrix strength vs Improvement
            modified = cluster_df[cluster_df['is_modified']]
            unmodified = cluster_df[~cluster_df['is_modified']]

            ax.scatter(modified['Polymer matrix Strength (MPa)'],
                      modified['Strength improvement (%)'],
                      color='green', alpha=0.6, label='Modified', s=50)
            ax.scatter(unmodified['Polymer matrix Strength (MPa)'],
                      unmodified['Strength improvement (%)'],
                      color='red', alpha=0.6, label='Unmodified', s=50)

            ax.set_xlabel('Matrix Strength (MPa)')
            ax.set_ylabel('Improvement (%)')
            ax.set_title(f'{cluster_id}: {self.clusters[cluster_id]["name"]}')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('output/cluster_summary.png', dpi=300)
        plt.close()

    def run_phase1_analysis(self):
        """Execute complete Phase 1 analysis pipeline"""
        print("Starting Phase 1 Strength Analysis...")

        # Step 1: Load and preprocess data
        self.load_and_preprocess_data()

        # Step 2: Assign clusters
        self.assign_clusters()

        # Step 3: Build graphs
        self.build_cluster_graphs()

        # Step 4: Calculate centrality
        self.calculate_centrality_metrics()

        # Step 5: Create visualizations
        self.visualize_cluster_graphs()

        # Step 6: Generate reports
        self.generate_summary_report()
        self.create_summary_figure()

        print("\nPhase 1 Strength analysis complete!")


if __name__ == "__main__":
    # Run the analysis
    analysis = StrengthClusteringAnalysis()
    analysis.run_phase1_analysis()
