"""
Visualize test results in table format
"""

import json
import sys
from typing import Dict, List


def print_table_separator(widths):
    """Print a table separator line"""
    print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")


def print_table_row(values, widths, align='left'):
    """Print a table row with proper alignment"""
    row = "|"
    for val, width in zip(values, widths):
        val_str = str(val)[:width]  # Truncate if too long
        if align == 'center':
            row += f" {val_str:^{width}} |"
        elif align == 'right':
            row += f" {val_str:>{width}} |"
        else:
            row += f" {val_str:<{width}} |"
    print(row)


def visualize_alpha_comparison(data: Dict):
    """Create a table comparing different alpha values"""
    print("\n" + "="*100)
    print("ALPHA WEIGHTING COMPARISON - Top Result per Query")
    print("="*100)

    alpha_values = data['metadata']['alpha_values_tested']

    # Column widths
    widths = [40, 10] + [15] * len(alpha_values)
    headers = ["Query", "Method"] + [f"α={a}" for a in alpha_values]

    print_table_separator(widths)
    print_table_row(headers, widths, align='center')
    print_table_separator(widths)

    for query_data in data['queries']:
        query = query_data['query'][:38]  # Truncate long queries

        # Show top result for each alpha
        hybrid_data = query_data['methods']['hybrid']

        # Top document ID for each alpha
        top_docs = []
        for alpha in alpha_values:
            alpha_key = f"alpha_{alpha}"
            if alpha_key in hybrid_data and len(hybrid_data[alpha_key]) > 0:
                top_result = hybrid_data[alpha_key][0]
                doc_num = top_result['doc_id'].replace('doc_', '')
                score = top_result['final_score']
                top_docs.append(f"doc_{doc_num}({score:.2f})")
            else:
                top_docs.append("N/A")

        row = [query, "Hybrid"] + top_docs
        print_table_row(row, widths)

    print_table_separator(widths)


def visualize_score_breakdown(data: Dict):
    """Create a detailed score breakdown table"""
    print("\n" + "="*120)
    print("SCORE BREAKDOWN - Semantic vs Keyword Contribution")
    print("="*120)

    for query_data in data['queries']:
        query = query_data['query']
        print(f"\nQuery: {query}")
        print("-" * 120)

        # Column widths
        widths = [10, 8, 40, 12, 12, 12]
        headers = ["Alpha", "Rank", "Document", "Final", "Semantic", "Keyword"]

        print_table_separator(widths)
        print_table_row(headers, widths, align='center')
        print_table_separator(widths)

        hybrid_data = query_data['methods']['hybrid']

        # Show results for alpha values 0.0, 0.5, 1.0 (keyword, balanced, semantic)
        for alpha in [0.0, 0.5, 1.0]:
            alpha_key = f"alpha_{alpha}"
            if alpha_key in hybrid_data:
                results = hybrid_data[alpha_key][:3]  # Top 3 results

                for i, result in enumerate(results):
                    alpha_display = f"{alpha}" if i == 0 else ""
                    doc_text = result['text'][:38] + "..."
                    row = [
                        alpha_display,
                        str(result['rank']),
                        doc_text,
                        f"{result['final_score']:.4f}",
                        f"{result['semantic_score']:.4f}",
                        f"{result['keyword_score']:.4f}"
                    ]
                    print_table_row(row, widths)

                if alpha != 1.0:  # Don't print separator after last alpha
                    print_table_separator(widths)

        print_table_separator(widths)


def visualize_method_comparison(data: Dict):
    """Compare semantic, keyword, and hybrid (balanced) methods"""
    print("\n" + "="*110)
    print("METHOD COMPARISON - Semantic vs Keyword vs Hybrid (α=0.5)")
    print("="*110)

    widths = [40, 15, 15, 15, 8]
    headers = ["Query", "Semantic Top", "Keyword Top", "Hybrid Top", "Match?"]

    print_table_separator(widths)
    print_table_row(headers, widths, align='center')
    print_table_separator(widths)

    for query_data in data['queries']:
        query = query_data['query'][:38]

        # Get top result from each method
        semantic_top = query_data['methods']['semantic'][0]['doc_id'] if query_data['methods']['semantic'] else "N/A"
        keyword_top = query_data['methods']['keyword'][0]['doc_id'] if query_data['methods']['keyword'] else "N/A"
        hybrid_top = query_data['methods']['hybrid']['alpha_0.5'][0]['doc_id'] if 'alpha_0.5' in query_data['methods']['hybrid'] else "N/A"

        # Check if all methods agree
        all_match = semantic_top == keyword_top == hybrid_top
        match_str = "✓ Yes" if all_match else "✗ No"

        row = [query, semantic_top, keyword_top, hybrid_top, match_str]
        print_table_row(row, widths)

    print_table_separator(widths)


def visualize_ranking_stability(data: Dict):
    """Show how rankings change across different alpha values"""
    print("\n" + "="*100)
    print("RANKING STABILITY - How top results change with alpha")
    print("="*100)

    for query_data in data['queries']:
        query = query_data['query']
        print(f"\nQuery: {query}")
        print("-" * 100)

        # Track which documents appear in top 3 for each alpha
        hybrid_data = query_data['methods']['hybrid']

        # Get unique docs that appear in top 3 across all alphas
        all_top_docs = set()
        for alpha_key in hybrid_data:
            for result in hybrid_data[alpha_key][:3]:
                all_top_docs.add(result['doc_id'])

        # Create table showing rank of each doc across alphas
        widths = [12, 60] + [8] * 5
        headers = ["Doc ID", "Text"] + ["α=0.0", "α=0.3", "α=0.5", "α=0.7", "α=1.0"]

        print_table_separator(widths)
        print_table_row(headers, widths, align='center')
        print_table_separator(widths)

        for doc_id in sorted(all_top_docs):
            # Get document text
            doc_num = int(doc_id.replace('doc_', ''))
            doc_text = data['documents'][doc_num][:58] + "..."

            # Get rank for each alpha
            ranks = []
            for alpha in [0.0, 0.3, 0.5, 0.7, 1.0]:
                alpha_key = f"alpha_{alpha}"
                rank = "-"
                for i, result in enumerate(hybrid_data[alpha_key], 1):
                    if result['doc_id'] == doc_id and i <= 3:
                        rank = str(i)
                        break
                ranks.append(rank)

            row = [doc_id, doc_text] + ranks
            print_table_row(row, widths)

        print_table_separator(widths)


def create_summary_report(data: Dict):
    """Create a summary report with key insights"""
    print("\n" + "="*100)
    print("SUMMARY REPORT")
    print("="*100 + "\n")

    print(f"Test Metadata:")
    print(f"  • Generated: {data['metadata']['generated_at']}")
    print(f"  • Documents: {data['metadata']['num_documents']}")
    print(f"  • Queries: {data['metadata']['num_queries']}")
    print(f"  • Alpha values tested: {data['metadata']['alpha_values_tested']}")

    # Analyze consensus across methods
    print(f"\nMethod Consensus Analysis:")
    consensus_count = 0
    for query_data in data['queries']:
        semantic_top = query_data['methods']['semantic'][0]['doc_id']
        keyword_top = query_data['methods']['keyword'][0]['doc_id'] if query_data['methods']['keyword'] else None
        hybrid_top = query_data['methods']['hybrid']['alpha_0.5'][0]['doc_id']

        if semantic_top == keyword_top == hybrid_top:
            consensus_count += 1

    print(f"  • Queries where all methods agree: {consensus_count}/{data['metadata']['num_queries']} ({consensus_count/data['metadata']['num_queries']*100:.1f}%)")

    # Analyze alpha stability
    print(f"\nAlpha Stability Analysis:")
    stable_queries = 0
    for query_data in data['queries']:
        hybrid_data = query_data['methods']['hybrid']
        top_docs = [hybrid_data[f"alpha_{a}"][0]['doc_id'] for a in data['metadata']['alpha_values_tested']]
        if len(set(top_docs)) == 1:
            stable_queries += 1

    print(f"  • Queries with same top result across all alphas: {stable_queries}/{data['metadata']['num_queries']} ({stable_queries/data['metadata']['num_queries']*100:.1f}%)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize_results.py <json_results_file>")
        print("\nExample:")
        print("  python visualize_results.py test_results_20251113_011002.json")
        sys.exit(1)

    json_file = sys.argv[1]

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{json_file}' is not a valid JSON file")
        sys.exit(1)

    print("\n" + "#"*100)
    print("#" + " "*98 + "#")
    print("#" + "HYBRID SEARCH RESULTS VISUALIZATION".center(98) + "#")
    print("#" + f"File: {json_file}".center(98) + "#")
    print("#" + " "*98 + "#")
    print("#"*100)

    # Generate all visualizations
    create_summary_report(data)
    visualize_alpha_comparison(data)
    visualize_method_comparison(data)
    visualize_score_breakdown(data)
    visualize_ranking_stability(data)

    print("\n" + "="*100)
    print("Visualization complete!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
