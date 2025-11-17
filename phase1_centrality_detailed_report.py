"""
Generate detailed centrality evaluation report for Phase 1
"""

import pandas as pd
import json
from phase1_modulus_clustering import ModulusClusteringAnalysis

# Run analysis to get centrality metrics
analysis = ModulusClusteringAnalysis()
analysis.load_and_preprocess_data()
analysis.assign_clusters()
analysis.build_cluster_graphs()
analysis.calculate_centrality_metrics()

# Create detailed report
report_lines = []
report_lines.append("="*80)
report_lines.append("PHASE 1: DETAILED CENTRALITY EVALUATION REPORT")
report_lines.append("="*80)
report_lines.append("\nCentrality metrics evaluate which polymer matrices act as 'knowledge hubs'")
report_lines.append("within each stiffness regime (C1-C4).\n")

# Create detailed tables for each cluster
for cluster_id in ['C1', 'C2', 'C3', 'C4']:
    if cluster_id not in analysis.centrality_metrics:
        continue
        
    metrics = analysis.centrality_metrics[cluster_id]
    report_lines.append(f"\n{'-'*80}")
    report_lines.append(f"CLUSTER {cluster_id}: {analysis.clusters[cluster_id]['name']} regime")
    report_lines.append(f"Range: {analysis.clusters[cluster_id]['range'][0]}-{analysis.clusters[cluster_id]['range'][1]} GPa")
    report_lines.append(f"{'-'*80}\n")
    
    # Create DataFrame for better formatting
    data = []
    for polymer in metrics['degree'].keys():
        data.append({
            'Polymer': polymer,
            'Degree Centrality': f"{metrics['degree'][polymer]:.4f}",
            'Weighted Degree': f"{metrics['weighted_degree'][polymer]:.2f}",
            'Betweenness Centrality': f"{metrics['betweenness'][polymer]:.4f}"
        })
    
    # Sort by weighted degree
    data.sort(key=lambda x: float(x['Weighted Degree']), reverse=True)
    
    # Print ALL polymers
    report_lines.append("ALL Polymers by Centrality Metrics:")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Polymer':<30} {'Degree Cent.':<15} {'Weighted Deg.':<15} {'Between. Cent.':<15}")
    report_lines.append("-" * 80)
    
    for i, row in enumerate(data):
        report_lines.append(f"{row['Polymer']:<30} {row['Degree Centrality']:<15} {row['Weighted Degree']:<15} {row['Betweenness Centrality']:<15}")
    
    # Summary statistics
    report_lines.append(f"\nCluster {cluster_id} Summary:")
    report_lines.append(f"- Total polymer types: {len(metrics['degree'])}")
    report_lines.append(f"- Highest weighted degree: {data[0]['Polymer']} ({data[0]['Weighted Degree']})")
    report_lines.append(f"- Average weighted degree: {sum(metrics['weighted_degree'].values())/len(metrics['weighted_degree']):.2f}")
    
    # Interpretation
    report_lines.append(f"\nInterpretation for {cluster_id}:")
    if cluster_id in ['C1', 'C2']:
        report_lines.append("- High weighted degree values indicate large property improvements")
        report_lines.append("- Soft/semi-soft systems show high variability in response")
    else:
        report_lines.append("- More consistent but lower improvement values")
        report_lines.append("- Dense networks indicate systematic reinforcement mechanisms")

# Modified vs Unmodified Analysis
report_lines.append(f"\n\n{'='*80}")
report_lines.append("MODIFIED VS UNMODIFIED CENTRALITY COMPARISON")
report_lines.append(f"{'='*80}\n")

comparison = analysis.compare_modified_vs_unmodified()
for cluster_id, comp in comparison.items():
    report_lines.append(f"\n{cluster_id}:")
    report_lines.append(f"  Modified systems: {comp['modified_count']} nodes")
    report_lines.append(f"  Unmodified systems: {comp['unmodified_count']} nodes")
    report_lines.append(f"  Avg improvement (modified): {comp['avg_mod_improvement']:.1f}%")
    report_lines.append(f"  Avg improvement (unmodified): {comp['avg_unmod_improvement']:.1f}%")
    
    if comp['avg_mod_improvement'] > comp['avg_unmod_improvement']:
        report_lines.append(f"  → Modified systems show {comp['avg_mod_improvement'] - comp['avg_unmod_improvement']:.1f}% higher improvement")
    else:
        report_lines.append(f"  → Unmodified systems show {comp['avg_unmod_improvement'] - comp['avg_mod_improvement']:.1f}% higher improvement")

# Save report
with open('phase1_output/centrality_evaluation_detailed.txt', 'w') as f:
    f.write('\n'.join(report_lines))

print("Detailed centrality evaluation report saved to phase1_output/centrality_evaluation_detailed.txt")

# Also create a JSON file with raw centrality data
centrality_data = {}
for cluster_id, metrics in analysis.centrality_metrics.items():
    centrality_data[cluster_id] = {
        'degree_centrality': metrics['degree'],
        'weighted_degree': metrics['weighted_degree'],
        'betweenness_centrality': metrics['betweenness']
    }

with open('phase1_output/centrality_raw_data.json', 'w') as f:
    json.dump(centrality_data, f, indent=2)
    
print("Raw centrality data saved to phase1_output/centrality_raw_data.json")