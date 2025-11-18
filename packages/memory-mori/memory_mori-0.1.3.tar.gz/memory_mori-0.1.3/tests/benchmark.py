"""
Performance Benchmarks
Measures latency and throughput of various operations
"""

import time
from typing import Dict, List, Callable
from datetime import datetime
from api import MemoryMori
from config import MemoryConfig


class Benchmark:
    """
    Performance benchmarking utilities.
    """

    @staticmethod
    def time_function(func: Callable, iterations: int = 10) -> Dict:
        """
        Measure function execution time.

        Args:
            func: Function to benchmark
            iterations: Number of iterations

        Returns:
            Dictionary with timing statistics
        """
        times = []

        for _ in range(iterations):
            start = time.time()
            func()
            end = time.time()
            times.append((end - start) * 1000)  # Convert to ms

        return {
            'iterations': iterations,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': sum(times) / len(times),
            'total_ms': sum(times),
            'times': times
        }

    @staticmethod
    def benchmark_store(mm: MemoryMori, num_docs: int = 100) -> Dict:
        """
        Benchmark document storage.

        Args:
            mm: MemoryMori instance
            num_docs: Number of documents to store

        Returns:
            Benchmark results
        """
        test_text = "This is a test document for benchmarking storage performance"

        start = time.time()
        for i in range(num_docs):
            mm.store(f"{test_text} {i}")
        end = time.time()

        total_time = (end - start) * 1000  # ms
        avg_time = total_time / num_docs

        return {
            'operation': 'store',
            'num_documents': num_docs,
            'total_time_ms': total_time,
            'avg_time_ms': avg_time,
            'throughput_docs_per_sec': num_docs / ((end - start) or 0.001)
        }

    @staticmethod
    def benchmark_retrieve(mm: MemoryMori, queries: List[str], max_items: int = 5) -> Dict:
        """
        Benchmark retrieval operations.

        Args:
            mm: MemoryMori instance
            queries: List of queries to test
            max_items: Number of items to retrieve

        Returns:
            Benchmark results
        """
        times = []

        for query in queries:
            start = time.time()
            mm.retrieve(query, max_items=max_items)
            end = time.time()
            times.append((end - start) * 1000)  # ms

        return {
            'operation': 'retrieve',
            'num_queries': len(queries),
            'max_items': max_items,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': sum(times) / len(times),
            'total_ms': sum(times),
            'throughput_queries_per_sec': len(queries) / (sum(times) / 1000)
        }

    @staticmethod
    def benchmark_get_context(mm: MemoryMori, queries: List[str], max_items: int = 5) -> Dict:
        """
        Benchmark context generation.

        Args:
            mm: MemoryMori instance
            queries: List of queries to test
            max_items: Number of items to include

        Returns:
            Benchmark results
        """
        times = []

        for query in queries:
            start = time.time()
            mm.get_context(query, max_items=max_items)
            end = time.time()
            times.append((end - start) * 1000)

        return {
            'operation': 'get_context',
            'num_queries': len(queries),
            'max_items': max_items,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': sum(times) / len(times),
            'total_ms': sum(times)
        }

    @staticmethod
    def benchmark_end_to_end(config: MemoryConfig = None, num_docs: int = 50) -> Dict:
        """
        Benchmark complete end-to-end workflow.

        Args:
            config: MemoryConfig (uses default if None)
            num_docs: Number of documents for testing

        Returns:
            Complete benchmark results
        """
        if config is None:
            config = MemoryConfig(
                collection_name="benchmark",
                persist_directory="./benchmark_data",
                profile_db_path="./benchmark_profile.db"
            )

        # Initialize
        start_init = time.time()
        mm = MemoryMori(config)
        init_time = (time.time() - start_init) * 1000

        # Benchmark storage
        store_results = Benchmark.benchmark_store(mm, num_docs)

        # Benchmark retrieval
        test_queries = [
            "Python programming",
            "web development",
            "machine learning",
            "data science",
            "containerization"
        ]
        retrieve_results = Benchmark.benchmark_retrieve(mm, test_queries)

        # Benchmark context generation
        context_results = Benchmark.benchmark_get_context(mm, test_queries)

        return {
            'initialization_ms': init_time,
            'store': store_results,
            'retrieve': retrieve_results,
            'get_context': context_results,
            'config': {
                'alpha': config.alpha,
                'lambda_decay': config.lambda_decay,
                'enable_entities': config.enable_entities,
                'enable_profile': config.enable_profile
            }
        }


def run_benchmark(verbose: bool = True, num_docs: int = 50) -> Dict:
    """
    Run complete performance benchmark suite.

    Args:
        verbose: Print detailed output
        num_docs: Number of documents for testing

    Returns:
        Benchmark results
    """
    if verbose:
        print("="*80)
        print("Performance Benchmarks")
        print("="*80)

    results = Benchmark.benchmark_end_to_end(num_docs=num_docs)

    if verbose:
        print(f"\nInitialization: {results['initialization_ms']:.2f} ms")

        print("\n" + "-"*80)
        print("STORAGE PERFORMANCE:")
        print("-"*80)
        store = results['store']
        print(f"Documents stored: {store['num_documents']}")
        print(f"Total time: {store['total_time_ms']:.2f} ms")
        print(f"Avg time per doc: {store['avg_time_ms']:.2f} ms")
        print(f"Throughput: {store['throughput_docs_per_sec']:.2f} docs/sec")

        print("\n" + "-"*80)
        print("RETRIEVAL PERFORMANCE:")
        print("-"*80)
        retrieve = results['retrieve']
        print(f"Queries tested: {retrieve['num_queries']}")
        print(f"Min time: {retrieve['min_ms']:.2f} ms")
        print(f"Max time: {retrieve['max_ms']:.2f} ms")
        print(f"Mean time: {retrieve['mean_ms']:.2f} ms")
        print(f"Throughput: {retrieve['throughput_queries_per_sec']:.2f} queries/sec")

        print("\n" + "-"*80)
        print("CONTEXT GENERATION PERFORMANCE:")
        print("-"*80)
        context = results['get_context']
        print(f"Queries tested: {context['num_queries']}")
        print(f"Min time: {context['min_ms']:.2f} ms")
        print(f"Max time: {context['max_ms']:.2f} ms")
        print(f"Mean time: {context['mean_ms']:.2f} ms")

    return results
