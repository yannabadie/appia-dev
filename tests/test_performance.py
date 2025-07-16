import os
"""Performance testing for critical JARVYS components."""

import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil


class PerformanceTest:
    """Individual performance test case."""

    def __init__(self, name: str, test_func: Callable, timeout: int = 30):
        self.name = name
        self.test_func = test_func
        self.timeout = timeout
        self.results = []

    def run(self, iterations: int = 5) -> Dict[str, Any]:
        """Run the performance test."""
        results = {
            "name": self.name,
            "iterations": iterations,
            "measurements": [],
            "statistics": {},
            "status": "success",
            "error": None,
        }

        for _i in range(iterations):
            try:
                start_time = time.perf_counter()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

                # Run test with timeout
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(self.test_func)
                    _result = future.result(timeout=self.timeout)

                end_time = time.perf_counter()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

                measurement = {
                    "iteration": i + 1,
                    "duration": end_time - start_time,
                    "memory_delta": end_memory - start_memory,
                    "result": (
                        result
                        if isinstance(result, (int, float, str, bool, type(None)))
                        else str(result)
                    ),
                }
                results["measurements"].append(measurement)

            except TimeoutError:
                results["status"] = "timeout"
                results["error"] = f"Test timed out after {self.timeout}s"
                break
            except Exception as e:
                results["status"] = "error"
                results["error"] = str(e)
                break

        # Calculate statistics
        if results["measurements"]:
            durations = [m["duration"] for m in results["measurements"]]
            memory_deltas = [m["memory_delta"] for m in results["measurements"]]

            results["statistics"] = {
                "duration": {
                    "mean": statistics.mean(durations),
                    "median": statistics.median(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "std_dev": (
                        statistics.stdev(durations) if len(durations) > 1 else 0
                    ),
                },
                "memory": {
                    "mean_delta": statistics.mean(memory_deltas),
                    "max_delta": max(memory_deltas),
                    "min_delta": min(memory_deltas),
                },
            }

        return results


class JarvysPerformanceTester:
    """Performance testing suite for JARVYS components."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_timestamp = datetime.now()
        self.system_info = self._get_system_info()

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "disk_usage": {
                "total_gb": psutil.disk_usage(self.project_root).total / (1024**3),
                "free_gb": psutil.disk_usage(self.project_root).free / (1024**3),
            },
        }

    def test_import_performance(self) -> bool:
        """Test module import performance."""
        modules = [
            "jarvys_dev.multi_model_router",
            "jarvys_dev.intelligent_orchestrator",
            "jarvys_dev.langgraph_loop",
        ]

        for module in modules:
            try:
                __import__(module)
            except ImportError:
                pass  # Module may not exist, that's ok for performance testing

        return True

    def test_config_loading_performance(self) -> bool:
        """Test configuration loading performance."""
        config_files = [
            self.project_root / "pyproject.toml",
            self.project_root / "src" / "jarvys_dev" / "model_config.json",
            self.project_root / "src" / "jarvys_dev" / "model_capabilities.json",
        ]

        for config_file in config_files:
            if config_file.exists():
                if config_file.suffix == ".json":
                    with open(config_file) as f:
                        json.load(f)
                elif config_file.suffix == ".toml":
                    with open(config_file) as f:
                        f.read()  # Simple read test

        return True

    def test_file_system_performance(self) -> int:
        """Test file system read/write performance."""
        test_file = self.project_root / "perf_test_temp.txt"
        test_data = "x" * 1024  # 1KB of data
        iterations = 100

        try:
            # Write test
            for _ in range(iterations):
                with open(test_file, "w") as f:
                    f.write(test_data)

            # Read test
            for _ in range(iterations):
                with open(test_file, "r") as f:
                    f.read()

            return iterations * 2  # Read + write operations
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_memory_usage_pattern(self) -> Dict[str, float]:
        """Test memory usage patterns."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Allocate some memory
        data = []
        for _i in range(1000):
            data.append("x" * 1024)  # 1KB strings

        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Release memory
        del data

        final_memory = psutil.Process().memory_info().rss / 1024 / 1024

        return {
            "initial_mb": initial_memory,
            "peak_mb": peak_memory,
            "final_mb": final_memory,
            "allocated_mb": peak_memory - initial_memory,
        }

    def test_concurrent_operations(self) -> int:
        """Test concurrent operation performance."""

        def dummy_task():
            time.sleep(0.01)  # 10ms task
            return sum(range(100))

        num_tasks = 20
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(dummy_task) for _ in range(num_tasks)]
            results = [future.result() for future in futures]

        end_time = time.perf_counter()
        end_time - start_time

        return len(results)  # Number of completed tasks

    def test_api_client_creation(self) -> bool:
        """Test API client = None creation performance."""
        try:
            # Test OpenAI client = None creation
            from openai import OpenAI

            _client = OpenAI(api_key="test-key")

            # Test Supabase client = None creation
            from supabase import create_client

            _supabase_client = create_client("https://test.supabase.co", "test-key")

            # Test GitHub client = None creation
            from github import Github

            Github("test-token")

            return True
        except ImportError:
            return False

    def test_json_processing_performance(self) -> int:
        """Test JSON processing performance."""
        # Create test data
        test_data = {
            "messages": [
                {"role": "user", "content": f"Test message {i}"} for _i in range(100)
            ],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "config = {}": {"temperature": 0.7, "max_tokens": 1000},
            },
        }

        operations = 0

        # Serialize/deserialize multiple times
        for _ in range(50):
            json_str = json.dumps(test_data)
            json.loads(json_str)
            operations += 2  # serialize + deserialize

        return operations

    def run_all_performance_tests(self, iterations: int = 3) -> Dict[str, Any]:
        """Run all performance tests."""
        tests = [
            PerformanceTest("import_performance", self.test_import_performance),
            PerformanceTest("config_loading", self.test_config_loading_performance),
            PerformanceTest("file_system_ops", self.test_file_system_performance),
            PerformanceTest("memory_patterns", self.test_memory_usage_pattern),
            PerformanceTest("concurrent_ops", self.test_concurrent_operations),
            PerformanceTest("api_client_creation", self.test_api_client_creation),
            PerformanceTest("json_processing", self.test_json_processing_performance),
        ]

        results = {
            "timestamp": self.test_timestamp.isoformat(),
            "system_info": self.system_info,
            "test_results": {},
            "summary": {
                "total_tests": len(tests),
                "passed": 0,
                "failed": 0,
                "timeouts": 0,
            },
        }

        for test in tests:
            print(f"Running {test.name}...")
            test_result = test.run(iterations)
            results["test_results"][test.name] = test_result

            # Update summary
            if test_result["status"] == "success":
                results["summary"]["passed"] += 1
            elif test_result["status"] == "timeout":
                results["summary"]["timeouts"] += 1
            else:
                results["summary"]["failed"] += 1

        return results

    def benchmark_component(
        self,
        component_name: str,
        test_func: Callable,
        load_levels: List[int] = None,
    ) -> Dict[str, Any]:
        """Benchmark a specific component under different load levels."""
        if load_levels is None:
            load_levels = [1, 5, 10, 20]

        benchmark_results = {
            "component": component_name,
            "timestamp": datetime.now().isoformat(),
            "load_tests": {},
        }

        for load_level in load_levels:
            print(f"Benchmarking {component_name} at load level {load_level}...")

            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024

            try:
                # Run test function with specified load
                _result = test_func(load_level)

                end_time = time.perf_counter()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024

                benchmark_results["load_tests"][load_level] = {
                    "duration": end_time - start_time,
                    "memory_delta": end_memory - start_memory,
                    "result": result,
                    "status": "success",
                }

            except Exception as e:
                benchmark_results["load_tests"][load_level] = {
                    "status": "error",
                    "error": str(e),
                }

        return benchmark_results

    def generate_performance_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive performance report."""
        results = self.run_all_performance_tests()

        if output_file:
            output_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f"performance_report_{timestamp}.json"

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        return str(output_path)

    def print_performance_summary(self):
        """Print human-readable performance summary."""
        results = self.run_all_performance_tests()

        print("⚡ JARVYS Performance Test Results")
        print("=" * 50)
        print(f"Test Time: {results['timestamp']}")
        print()

        print("🖥️  System Information:")
        sys_info = results["system_info"]
        print(f"  Python: {sys_info['python_version']}")
        print(f"  Platform: {sys_info['platform']}")
        print(f"  CPU Cores: {sys_info['cpu_count']}")
        print(f"  Memory: {sys_info['memory_total_mb']:.0f} MB")
        print(f"  Disk Free: {sys_info['disk_usage']['free_gb']:.1f} GB")
        print()

        print("📊 Test Summary:")
        summary = results["summary"]
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  ✅ Passed: {summary['passed']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  ⏰ Timeouts: {summary['timeouts']}")
        print()

        print("⏱️  Performance Results:")
        for test_name, test_result in results["test_results"].items():
            if test_result["status"] == "success" and "statistics" in test_result:
                stats = test_result["statistics"]
                duration_stats = stats.get("duration", {})
                mean_time = duration_stats.get("mean", 0)

                status_icon = (
                    "✅" if mean_time < 1.0 else "⚠️" if mean_time < 5.0 else "❌"
                )
                print(
                    f"  {status_icon} {test_name.replace('_', ' ').title()}: {mean_time:.3f}s avg"
                )

                if mean_time > 1.0:
                    print(
                        f"    Range: {duration_stats.get('min', 0):.3f}s - {duration_stats.get('max', 0):.3f}s"
                    )
            else:
                print(
                    f"  ❌ {test_name.replace('_', ' ').title()}: {test_result['status']}"
                )

        print()

        # Performance recommendations
        print("💡 Performance Recommendations:")
        slow_tests = [
            name
            for name, result in results["test_results"].items()
            if result["status"] == "success"
            and result.get("statistics", {}).get("duration", {}).get("mean", 0) > 1.0
        ]

        if slow_tests:
            print(f"  - Optimize slow operations: {', '.join(slow_tests)}")

        failed_tests = [
            name
            for name, result in results["test_results"].items()
            if result["status"] != "success"
        ]

        if failed_tests:
            print(f"  - Fix failing tests: {', '.join(failed_tests)}")

        if not slow_tests and not failed_tests:
            print("  - Performance looks good!")

        print()


def main():
    """Main entry point for performance tester."""
    tester = JarvysPerformanceTester()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report_path = tester.generate_performance_report(output_file)
            print(f"Performance report saved to: {report_path}")

        elif command == "json":
            results = tester.run_all_performance_tests()
            print(json.dumps(results, indent=2, default=str))

        elif command == "test" or command == "run":
            tester.print_performance_summary()

        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python test_performance.py [report|json|test|run] [output_file]"
            )
    else:
        tester.print_performance_summary()


if __name__ == "__main__":
    main()
