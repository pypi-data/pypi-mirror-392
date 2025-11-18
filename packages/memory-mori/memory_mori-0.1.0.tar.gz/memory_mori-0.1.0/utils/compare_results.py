"""
Utility script to compare results from different test runs
"""

import sys
import re
from typing import List, Dict


def parse_results_file(filename: str) -> Dict:
    """Parse a search results file and extract key metrics"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    results = {
        'filename': filename,
        'queries': []
    }

    # Extract queries and their results
    query_pattern = r'QUERY: (.+?)\n'
    queries = re.findall(query_pattern, content)

    for query in queries:
        # Find hybrid results for this query
        query_section = content.split(f'QUERY: {query}')[1].split('QUERY:')[0]

        # Extract top result from hybrid search
        hybrid_section = re.search(
            r'Hybrid Search Results \(alpha=0\.7\).*?\[1\] ID: ([\w_]+).*?Text: (.+?)\.\.\..*?Final Score: ([\d.]+)',
            query_section,
            re.DOTALL
        )

        if hybrid_section:
            results['queries'].append({
                'query': query,
                'top_result_id': hybrid_section.group(1),
                'top_result_text': hybrid_section.group(2),
                'top_score': float(hybrid_section.group(3))
            })

    return results


def compare_files(file1: str, file2: str):
    """Compare two result files side by side"""
    print(f"\nComparing Results:")
    print(f"{'='*80}")
    print(f"File 1: {file1}")
    print(f"File 2: {file2}")
    print(f"{'='*80}\n")

    results1 = parse_results_file(file1)
    results2 = parse_results_file(file2)

    # Compare query by query
    for i, (q1, q2) in enumerate(zip(results1['queries'], results2['queries']), 1):
        print(f"\nQuery {i}: {q1['query']}")
        print(f"{'-'*80}")

        print(f"\nFile 1 Top Result:")
        print(f"  ID: {q1['top_result_id']}")
        print(f"  Text: {q1['top_result_text']}")
        print(f"  Score: {q1['top_score']:.4f}")

        print(f"\nFile 2 Top Result:")
        print(f"  ID: {q2['top_result_id']}")
        print(f"  Text: {q2['top_result_text']}")
        print(f"  Score: {q2['top_score']:.4f}")

        # Check if results match
        if q1['top_result_id'] == q2['top_result_id']:
            print(f"\n  ✓ Same top result")
        else:
            print(f"\n  ✗ Different top results!")

        score_diff = abs(q1['top_score'] - q2['top_score'])
        if score_diff < 0.01:
            print(f"  ✓ Similar scores (diff: {score_diff:.4f})")
        else:
            print(f"  ⚠ Score difference: {score_diff:.4f}")


def summarize_file(filename: str):
    """Display a summary of a results file"""
    print(f"\nSummary of: {filename}")
    print(f"{'='*80}\n")

    results = parse_results_file(filename)

    for i, query_result in enumerate(results['queries'], 1):
        print(f"{i}. Query: {query_result['query']}")
        print(f"   Top Result: {query_result['top_result_text'][:60]}...")
        print(f"   Score: {query_result['top_score']:.4f}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python compare_results.py <result_file>")
        print("  python compare_results.py <result_file1> <result_file2>")
        print("\nExamples:")
        print("  python compare_results.py search_results_20251113_011002.txt")
        print("  python compare_results.py results1.txt results2.txt")
        sys.exit(1)

    if len(sys.argv) == 2:
        # Single file - show summary
        summarize_file(sys.argv[1])
    elif len(sys.argv) == 3:
        # Two files - compare them
        compare_files(sys.argv[1], sys.argv[2])
    else:
        print("Error: Too many arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
