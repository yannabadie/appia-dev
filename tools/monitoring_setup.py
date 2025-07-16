"""Monitoring setup and configuration for JARVYS ecosystem."""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import schedule


class JarvysMonitoringSetup:
    """Setup and configure monitoring for JARVYS ecosystem."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.monitoring_config = self._load_monitoring_config()
        self.metrics_db_path = self.project_root / "jarvys_metrics.db"

    def _load_monitoring_config(self) -> Dict[str, Any]:
        """Load monitoring configuration."""
        return {
            "metrics_collection": {
                "enabled": True,
                "interval_minutes": 5,
                "retention_days": 30,
            },
            "health_checks": {
                "enabled": True,
                "interval_minutes": 10,
                "endpoints": ["openai_api", "supabase_api", "github_api"],
            },
            "error_tracking": {
                "enabled": True,
                "scan_interval_hours": 1,
                "severity_threshold": "medium",
            },
            "performance_monitoring": {
                "enabled": True,
                "benchmark_interval_hours": 24,
                "alert_threshold_seconds": 5.0,
            },
            "alerts": {
                "enabled": False,  # Would need external service
                "channels": ["console", "file"],
                "critical_threshold": 5,
                "warning_threshold": 10,
            },
        }

    def setup_metrics_database(self) -> bool:
        """Set up SQLite database for metrics storage."""
        try:
            conn = sqlite3.connect(self.metrics_db_path)
            cursor = conn.cursor()

            # Create metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL,
                    metadata TEXT,
                    component TEXT
                )
            """
            )

            # Create health_checks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    error_message TEXT,
                    details TEXT
                )
            """
            )

            # Create error_log table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS error_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    severity TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    location TEXT,
                    context TEXT
                )
            """
            )

            # Create performance_benchmarks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    test_name TEXT NOT NULL,
                    duration REAL NOT NULL,
                    memory_usage REAL,
                    status TEXT,
                    details TEXT
                )
            """
            )

            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_checks(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_log(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_benchmarks(timestamp)"
            )

            conn.commit()
            conn.close()

            print(f"✅ Metrics database initialized: {self.metrics_db_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to setup metrics database: {e}")
            return False

    def record_metric(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        metadata: Optional[Dict] = None,
        component: str = "system",
    ) -> bool:
        """Record a metric in the database."""
        try:
            conn = sqlite3.connect(self.metrics_db_path)
            cursor = conn.cursor()

            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute(
                """
                INSERT INTO metrics (metric_type, metric_name, value, metadata, component)
                VALUES (?, ?, ?, ?, ?)
            """,
                (metric_type, metric_name, value, metadata_json, component),
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"❌ Failed to record metric: {e}")
            return False

    def record_health_check(
        self,
        component: str,
        status: str,
        response_time: float = None,
        error_message: str = None,
        details: Dict = None,
    ) -> bool:
        """Record a health check result."""
        try:
            conn = sqlite3.connect(self.metrics_db_path)
            cursor = conn.cursor()

            details_json = json.dumps(details) if details else None

            cursor.execute(
                """
                INSERT INTO health_checks (component, status, response_time, error_message, details)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    component,
                    status,
                    response_time,
                    error_message,
                    details_json,
                ),
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"❌ Failed to record health check: {e}")
            return False

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        metrics = {}

        try:
            import psutil

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["cpu_usage"] = cpu_percent
            self.record_metric("system", "cpu_usage_percent", cpu_percent)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_mb = memory.used / 1024 / 1024
            metrics["memory_usage_percent"] = memory_percent
            metrics["memory_usage_mb"] = memory_mb
            self.record_metric("system", "memory_usage_percent", memory_percent)
            self.record_metric("system", "memory_usage_mb", memory_mb)

            # Disk metrics
            disk = psutil.disk_usage(self.project_root)
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            metrics["disk_usage_percent"] = disk_percent
            metrics["disk_free_gb"] = disk_free_gb
            self.record_metric("system", "disk_usage_percent", disk_percent)
            self.record_metric("system", "disk_free_gb", disk_free_gb)

        except ImportError:
            print("⚠️  psutil not available for system metrics")

        return metrics

    def run_health_checks(self) -> Dict[str, Any]:
        """Run health checks on all components."""
        health_results = {}

        # Check OpenAI API
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                # Initialize client = None properly
                import openai

                client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
                models = client.models.list()

                start_time = time.time()
                response_time = time.time() - start_time

                health_results["openai_api"] = {
                    "status": "healthy",
                    "response_time": response_time,
                    "models_count": len(models.data),
                }
                self.record_health_check(
                    "openai_api",
                    "healthy",
                    response_time,
                    details={"models_count": len(models.data)},
                )

            except Exception as e:
                health_results["openai_api"] = {
                    "status": "unhealthy",
                    "error": str(e)[:100],
                }
                self.record_health_check(
                    "openai_api", "unhealthy", error_message=str(e)[:100]
                )
        else:
            health_results["openai_api"] = {"status": "not_configured"}
            self.record_health_check("openai_api", "not_configured")

        # Check Supabase API
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                from supabase import create_client

                client = create_client(supabase_url, supabase_key)

                start_time = time.time()
                client.table("health_check").select("*").limit(1).execute()
                response_time = time.time() - start_time

                health_results["supabase_api"] = {
                    "status": "healthy",
                    "response_time": response_time,
                }
                self.record_health_check("supabase_api", "healthy", response_time)

            except Exception as e:
                error_str = str(e).lower()
                if "relation" in error_str and "does not exist" in error_str:
                    health_results["supabase_api"] = {
                        "status": "healthy",
                        "note": "Connected (table doesn't exist - normal)",
                    }
                    self.record_health_check("supabase_api", "healthy")
                else:
                    health_results["supabase_api"] = {
                        "status": "unhealthy",
                        "error": str(e)[:100],
                    }
                    self.record_health_check(
                        "supabase_api", "unhealthy", error_message=str(e)[:100]
                    )
        else:
            health_results["supabase_api"] = {"status": "not_configured"}
            self.record_health_check("supabase_api", "not_configured")

        return health_results

    def cleanup_old_data(self, retention_days: int = 30) -> Dict[str, int]:
        """Clean up old monitoring data."""
        cleanup_results = {}
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        try:
            conn = sqlite3.connect(self.metrics_db_path)
            cursor = conn.cursor()

            # Clean up old metrics
            cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_date,))
            cleanup_results["metrics_deleted"] = cursor.rowcount

            # Clean up old health checks
            cursor.execute(
                "DELETE FROM health_checks WHERE timestamp < ?", (cutoff_date,)
            )
            cleanup_results["health_checks_deleted"] = cursor.rowcount

            # Clean up old error logs
            cursor.execute("DELETE FROM error_log WHERE timestamp < ?", (cutoff_date,))
            cleanup_results["error_logs_deleted"] = cursor.rowcount

            # Clean up old performance benchmarks
            cursor.execute(
                "DELETE FROM performance_benchmarks WHERE timestamp < ?",
                (cutoff_date,),
            )
            cleanup_results["benchmarks_deleted"] = cursor.rowcount

            conn.commit()
            conn.close()

        except Exception as e:
            cleanup_results["error"] = str(e)

        return cleanup_results

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring system status."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "database": {
                "exists": self.metrics_db_path.exists(),
                "size_mb": 0,
                "tables": [],
            },
            "configuration": self.monitoring_config,
            "recent_activity": {},
        }

        if self.metrics_db_path.exists():
            status["database"]["size_mb"] = self.metrics_db_path.stat().st_size / (
                1024 * 1024
            )

            try:
                conn = sqlite3.connect(self.metrics_db_path)
                cursor = conn.cursor()

                # Check tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                status["database"]["tables"] = tables

                # Get recent activity counts
                for table in tables:
                    if table in [
                        "metrics",
                        "health_checks",
                        "error_log",
                        "performance_benchmarks",
                    ]:
                        cursor.execute(
                            f'SELECT COUNT(*) FROM {table} WHERE timestamp > datetime("now", "-24 hours")'
                        )
                        count = cursor.fetchone()[0]
                        status["recent_activity"][f"{table}_24h"] = count

                conn.close()

            except Exception as e:
                status["database"]["error"] = str(e)

        return status

    def setup_scheduled_monitoring(self) -> bool:
        """Set up scheduled monitoring tasks."""
        try:
            config = self.monitoring_config

            # Schedule metrics collection
            if config["metrics_collection"]["enabled"]:
                interval = config["metrics_collection"]["interval_minutes"]
                schedule.every(interval).minutes.do(self.collect_system_metrics)
                print(f"✅ Scheduled metrics collection every {interval} minutes")

            # Schedule health checks
            if config["health_checks"]["enabled"]:
                interval = config["health_checks"]["interval_minutes"]
                schedule.every(interval).minutes.do(self.run_health_checks)
                print(f"✅ Scheduled health checks every {interval} minutes")

            # Schedule cleanup
            schedule.every().day.at("02:00").do(self.cleanup_old_data)
            print("✅ Scheduled daily cleanup at 2:00 AM")

            return True

        except Exception as e:
            print(f"❌ Failed to setup scheduled monitoring: {e}")
            return False

    def run_monitoring_daemon(self, duration_minutes: int = None):
        """Run monitoring daemon."""
        print("🔄 Starting JARVYS monitoring daemon...")

        if not self.setup_scheduled_monitoring():
            return

        start_time = time.time()

        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds

                # Exit after specified duration
                if duration_minutes:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= duration_minutes:
                        print(
                            f"✅ Monitoring daemon completed {duration_minutes} minute run"
                        )
                        break

        except KeyboardInterrupt:
            print("\n⏹️  Monitoring daemon stopped by user")
        except Exception as e:
            print(f"❌ Monitoring daemon error: {e}")

    def generate_monitoring_report(self, output_file: Optional[str] = None) -> str:
        """Generate monitoring status report."""
        status = self.get_monitoring_status()

        # Add recent metrics
        if self.metrics_db_path.exists():
            try:
                conn = sqlite3.connect(self.metrics_db_path)
                cursor = conn.cursor()

                # Get latest metrics
                cursor.execute(
                    """
                    SELECT metric_type, metric_name, value, timestamp 
                    FROM metrics 
                    WHERE timestamp > datetime("now", "-1 hour")
                    ORDER BY timestamp DESC LIMIT 50
                """
                )
                status["recent_metrics"] = [
                    {
                        "type": row[0],
                        "name": row[1],
                        "value": row[2],
                        "timestamp": row[3],
                    }
                    for row in cursor.fetchall()
                ]

                # Get health check summary
                cursor.execute(
                    """
                    SELECT component, status, COUNT(*) as count
                    FROM health_checks 
                    WHERE timestamp > datetime("now", "-24 hours")
                    GROUP BY component, status
                """
                )
                status["health_summary"] = [
                    {"component": row[0], "status": row[1], "count": row[2]}
                    for row in cursor.fetchall()
                ]

                conn.close()

            except Exception as e:
                status["metrics_error"] = str(e)

        if output_file:
            output_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f"monitoring_report_{timestamp}.json"

        with open(output_path, "w") as f:
            json.dump(status, f, indent=2, default=str)

        return str(output_path)

    def print_monitoring_summary(self):
        """Print human-readable monitoring summary."""
        status = self.get_monitoring_status()

        print("📊 JARVYS Monitoring System Status")
        print("=" * 50)
        print(f"Status Time: {status['timestamp']}")
        print()

        # Database status
        db_status = status["database"]
        print("🗄️  Database Status:")
        if db_status["exists"]:
            print(f"  ✅ Database exists: {self.metrics_db_path}")
            print(f"  📦 Size: {db_status['size_mb']:.2f} MB")
            print(f"  📋 Tables: {', '.join(db_status['tables'])}")
        else:
            print(f"  ❌ Database not found: {self.metrics_db_path}")
        print()

        # Recent activity
        if status["recent_activity"]:
            print("📈 Recent Activity (24 hours):")
            for activity, count in status["recent_activity"].items():
                activity_name = activity.replace("_24h", "").replace("_", " ").title()
                print(f"  {activity_name}: {count}")
            print()

        # Configuration
        config = status["configuration"]
        print("⚙️  Configuration:")
        for category, settings in config.items():
            if isinstance(settings, dict) and "enabled" in settings:
                enabled_status = "✅" if settings["enabled"] else "❌"
                print(
                    f"  {enabled_status} {category.replace('_', ' ').title()}: {settings['enabled']}"
                )
        print()


def main():
    """Main entry point for monitoring setup."""
    monitor = JarvysMonitoringSetup()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "setup":
            success = monitor.setup_metrics_database()
            if success:
                print("✅ Monitoring setup complete")
            else:
                print("❌ Monitoring setup failed")

        elif command == "status":
            monitor.print_monitoring_summary()

        elif command == "collect":
            metrics = monitor.collect_system_metrics()
            print(f"📊 Collected metrics: {metrics}")

        elif command == "health":
            health = monitor.run_health_checks()
            print(f"🏥 Health check results: {health}")

        elif command == "daemon":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else None
            monitor.run_monitoring_daemon(duration)

        elif command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report_path = monitor.generate_monitoring_report(output_file)
            print(f"📋 Monitoring report saved to: {report_path}")

        elif command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            results = monitor.cleanup_old_data(days)
            print(f"🧹 Cleanup results: {results}")

        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python monitoring_setup.py [setup|status|collect|health|daemon|report|cleanup] [args]"
            )
    else:
        monitor.print_monitoring_summary()


if __name__ == "__main__":
    try:
        import schedule
    except ImportError:
        print("❌ Missing dependencies. Install with: pip install schedule psutil")
        sys.exit(1)

    main()
