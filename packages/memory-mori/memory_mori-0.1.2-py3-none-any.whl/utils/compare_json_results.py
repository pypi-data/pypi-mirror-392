"""
Compare two JSON test result files side by side
Useful for A/B testing different configurations
"""

import json
import sys


def load_json_results(filename):
    """Load JSON results file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{filename}' is not a valid JSON file")
        sys.exit(1)


def compare_top_results(data1, data2, alpha=0.7):
    """Compare top results between two test runs"""
    print("\n" + "="*100)
    print(f"TOP RESULT COMPARISON (α={alpha})")
    print("="*100 + "\n")

    # Create table
    widths = [40, 20, 20, 10]
    headers = ["Query", "File 1 Top Result", "File 2 Top Result", "Match?"]

    # Print header
    print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")
    print("|" + "|".join([f" {h:^{w}} " for h, w in zip(headers, widths)]) + "|")
    print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")

    matches = 0
    total = 0

    for q1, q2 in zip(data1['queries'], data2['queries']):
        query = q1['query'][:38]
        alpha_key = f"alpha_{alpha}"

        # Get top results
        top1 = q1['methods']['hybrid'][alpha_key][0]['doc_id']
        top2 = q2['methods']['hybrid'][alpha_key][0]['doc_id']

        match = "✓ Yes" if top1 == top2 else "✗ No"
        if top1 == top2:
            matches += 1
        total += 1

        row = [query, top1, top2, match]
        print("|" + "|".join([f" {str(v):<{w}} " for v, w in zip(row, widths)]) + "|")

    print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")
    print(f"\nAgreement: {matches}/{total} ({matches/total*100:.1f}%)")


def compare_score_differences(data1, data2, alpha=0.7):
    """Compare score differences for matching queries"""
    print("\n" + "="*100)
    print(f"SCORE DIFFERENCE ANALYSIS (α={alpha})")
    print("="*100 + "\n")

    widths = [40, 15, 15, 15]
    headers = ["Query", "File 1 Score", "File 2 Score", "Difference"]

    print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")
    print("|" + "|".join([f" {h:^{w}} " for h, w in zip(headers, widths)]) + "|")
    print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")

    alpha_key = f"alpha_{alpha}"

    for q1, q2 in zip(data1['queries'], data2['queries']):
        query = q1['query'][:38]

        score1 = q1['methods']['hybrid'][alpha_key][0]['final_score']
        score2 = q2['methods']['hybrid'][alpha_key][0]['final_score']
        diff = abs(score1 - score2)

        row = [query, f"{score1:.4f}", f"{score2:.4f}", f"{diff:.4f}"]
        print("|" + "|".join([f" {str(v):<{w}} " for v, w in zip(row, widths)]) + "|")

    print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")


def compare_ranking_changes(data1, data2, alpha=0.7):
    """Show ranking changes for top documents"""
    print("\n" + "="*100)
    print(f"RANKING CHANGES (α={alpha})")
    print("="*100)

    alpha_key = f"alpha_{alpha}"

    for q1, q2 in zip(data1['queries'], data2['queries']):
        query = q1['query']
        print(f"\nQuery: {query}")
        print("-" * 100)

        # Get top 3 from each
        results1 = {r['doc_id']: r['rank'] for r in q1['methods']['hybrid'][alpha_key][:3]}
        results2 = {r['doc_id']: r['rank'] for r in q2['methods']['hybrid'][alpha_key][:3]}

        # Get all unique docs
        all_docs = set(results1.keys()) | set(results2.keys())

        widths = [15, 60, 12, 12]
        headers = ["Doc ID", "Text", "File 1 Rank", "File 2 Rank"]

        print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")
        print("|" + "|".join([f" {h:^{w}} " for h, w in zip(headers, widths)]) + "|")
        print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")

        for doc_id in sorted(all_docs):
            doc_num = int(doc_id.replace('doc_', ''))
            doc_text = data1['documents'][doc_num][:58] + "..."

            rank1 = results1.get(doc_id, "-")
            rank2 = results2.get(doc_id, "-")

            row = [doc_id, doc_text, str(rank1), str(rank2)]
            print("|" + "|".join([f" {str(v):<{w}} " for v, w in zip(row, widths)]) + "|")

        print("+" + "+".join(["-" * (w + 2) for w in widths]) + "+")


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_json_results.py <file1.json> <file2.json>")
        print("\nExample:")
        print("  python compare_json_results.py test_results_v1.json test_results_v2.json")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    print("\n" + "#"*100)
    print("#" + " "*98 + "#")
    print("#" + "JSON TEST RESULTS COMPARISON".center(98) + "#")
    print("#" + " "*98 + "#")
    print("#" + f"File 1: {file1}".ljust(98) + "#")
    print("#" + f"File 2: {file2}".ljust(98) + "#")
    print("#" + " "*98 + "#")
    print("#"*100)

    data1 = load_json_results(file1)
    data2 = load_json_results(file2)

    # Validate same queries
    if len(data1['queries']) != len(data2['queries']):
        print("\nWarning: Files have different number of queries!")

    # Compare for different alpha values
    print("\n" + "="*100)
    print("TESTING MULTIPLE ALPHA VALUES")
    print("="*100)

    for alpha in [0.0, 0.5, 0.7, 1.0]:
        compare_top_results(data1, data2, alpha=alpha)

    # Detailed comparisons for default alpha
    compare_score_differences(data1, data2, alpha=0.7)
    compare_ranking_changes(data1, data2, alpha=0.7)

    print("\n" + "="*100)
    print("Comparison complete!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
