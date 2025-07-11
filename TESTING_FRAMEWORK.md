# JARVYS Testing and Debugging Framework

## Overview

This comprehensive testing and debugging framework provides complete validation and monitoring capabilities for the JARVYS ecosystem, including JARVYS_DEV (cloud agent) and JARVYS_AI (local agent) components.

## Framework Components

### 🧪 Testing Suite

#### Environment & Infrastructure Tests
- **`tests/test_environment.py`**: Validates Python environment, dependencies, and project structure
- **`tests/test_connectivity.py`**: Tests connectivity to external APIs (OpenAI, Supabase, GitHub, Gemini, Anthropic)
- **`tests/test_docker.py`**: Validates Docker and containerization setup
- **`tests/test_infrastructure.py`**: Tests Supabase, GCP, and cloud infrastructure components

#### Core Application Tests
- **`tests/test_jarvys_dev.py`**: Tests JARVYS_DEV cloud agent functionality
- **`tests/test_jarvys_ai.py`**: Tests JARVYS_AI local agent features
- **`tests/test_agent_communication.py`**: Tests memory sharing and inter-agent communication

#### Workflow & Integration Tests
- **`tests/test_workflows.py`**: Validates GitHub Actions workflows and YAML syntax
- **`tests/test_automation.py`**: Tests cron schedules, CI/CD pipeline, and automation
- **`tests/test_deployment.py`**: Tests Supabase, Cloud Build, and Docker deployments
- **`tests/test_api_integration.py`**: Tests API endpoints, MCP server, and external integrations

#### Performance Tests
- **`tests/test_performance.py`**: Load testing and performance benchmarking

### 🔧 Debugging Tools

#### Interactive Debugging
- **`tools/debug_dashboard.py`**: Interactive debugging interface with comprehensive diagnostics
- **`tools/health_check.py`**: System health monitoring with component status
- **`tools/log_analyzer.py`**: Centralized log analysis and pattern detection
- **`tools/error_tracker.py`**: Error detection and reporting with severity classification

#### Monitoring & Metrics
- **`tools/monitoring_setup.py`**: Complete monitoring system with SQLite database and scheduled tasks

## Quick Start

### 1. Install Dependencies

```bash
# Install with Poetry (recommended)
poetry install --with dev

# Or with pip
pip install -r requirements.txt
pip install pytest pytest-mock pre-commit mkdocs-material
```

### 2. Run Basic Tests

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/test_environment.py -v
poetry run pytest tests/test_connectivity.py -v
poetry run pytest -m "not integration" -v  # Skip integration tests

# Run integration tests (requires credentials)
poetry run pytest -m integration -v
```

### 3. Use Debugging Tools

```bash
# Interactive debug dashboard
python tools/debug_dashboard.py

# System health check
python tools/health_check.py

# Error detection scan
python tools/error_tracker.py scan

# Log analysis
python tools/log_analyzer.py

# Performance testing
python tests/test_performance.py

# Setup monitoring
python tools/monitoring_setup.py setup
```

## Environment Configuration

### Required Environment Variables

```bash
# Core API Keys
export OPENAI_API_KEY="sk-..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="eyJ..."

# Optional for Full Functionality
export GITHUB_TOKEN="ghp_..."
export GEMINI_API_KEY="AIza..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GCP_SA_JSON='{"type": "service_account"...}'
export SUPABASE_PROJECT_REF="xxx"
export SUPABASE_ACCESS_TOKEN="sbp_..."
```

### Test Configuration

The framework gracefully handles missing credentials:
- Tests skip when required credentials are unavailable
- Integration tests are marked separately for optional execution
- Environment validation provides clear feedback on missing configuration

## Test Categories

### Integration Tests
Tests marked with `@pytest.mark.integration` require external service credentials:

```bash
# Run without integration tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration
```

### Security Tests
- Secret exposure detection
- Authentication validation
- Permission verification
- Workflow security checks

### Performance Tests
- API response time measurement
- Memory usage analysis
- Concurrent operation testing
- File system performance

## Debugging Workflow

### 1. Quick Health Check

```bash
python tools/health_check.py
```

**Output Example:**
```
🏥 JARVYS Health Check Summary
Overall Status: WARNING
✅ Environment: healthy
⚠️ APIs: warning (missing credentials)
✅ Services: healthy
```

### 2. Error Detection

```bash
python tools/error_tracker.py scan
```

**Detects:**
- API authentication failures
- Missing dependencies
- Configuration errors
- Secret exposure in logs
- Network connectivity issues

### 3. Log Analysis

```bash
python tools/log_analyzer.py
```

**Features:**
- Automatic log file discovery
- Error pattern detection
- Keyword frequency analysis
- Recent activity summaries

### 4. Performance Analysis

```bash
python tests/test_performance.py
```

**Benchmarks:**
- Module import performance
- Configuration loading
- File system operations
- Memory usage patterns
- Concurrent operations

## Monitoring System

### Setup Monitoring Database

```bash
python tools/monitoring_setup.py setup
```

Creates SQLite database with tables for:
- System metrics (CPU, memory, disk)
- Health check results
- Error logs
- Performance benchmarks

### Continuous Monitoring

```bash
# Run monitoring daemon for 60 minutes
python tools/monitoring_setup.py daemon 60

# Check monitoring status
python tools/monitoring_setup.py status
```

### Generate Reports

```bash
# Health report
python tools/health_check.py report health_report.json

# Error report
python tools/error_tracker.py report error_report.json

# Performance report
python tests/test_performance.py report performance_report.json

# Monitoring report
python tools/monitoring_setup.py report monitoring_report.json
```

## GitHub Actions Integration

### Workflow Testing

The framework validates all GitHub Actions workflows:

```bash
pytest tests/test_workflows.py -v
```

**Validates:**
- YAML syntax correctness
- Required workflow presence
- Security configurations
- Cron schedule formats
- Permission restrictions

### Automation Testing

```bash
pytest tests/test_automation.py -v
```

**Tests:**
- Scheduled execution patterns
- CI/CD pipeline stages
- Deployment automation
- Error handling mechanisms

## Advanced Usage

### Custom Test Configuration

Create `pytest.ini` customizations:

```ini
[pytest]
testpaths = tests
pythonpath = src
markers = 
    integration: marks tests as integration tests
    slow: marks tests as slow running
    security: marks tests as security related
```

### Performance Benchmarking

```python
from tests.test_performance import JarvysPerformanceTester

tester = JarvysPerformanceTester()

# Benchmark specific component
results = tester.benchmark_component(
    "api_calls", 
    lambda load: make_api_calls(load),
    load_levels=[1, 5, 10, 20]
)
```

### Custom Error Patterns

```python
from tools.error_tracker import JarvysErrorTracker, ErrorPattern, ErrorSeverity

tracker = JarvysErrorTracker()

# Add custom error pattern
custom_pattern = ErrorPattern(
    name="custom_error",
    pattern=r"(?i)(custom.*error.*pattern)",
    severity=ErrorSeverity.HIGH,
    description="Custom error description",
    suggested_fix="Custom fix suggestion"
)

tracker.error_patterns.append(custom_pattern)
```

## CI/CD Integration

### Pre-commit Hooks

```bash
# Install pre-commit
pre-commit install

# Run on changed files
pre-commit run --files tests/test_*.py

# Run all tools
pre-commit run --all-files
```

### GitHub Actions

The framework integrates with existing workflows:

```yaml
# In .github/workflows/ci.yml
- name: Run comprehensive tests
  run: |
    poetry run pytest tests/ -v
    python tools/health_check.py
    python tools/error_tracker.py scan
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` is in Python path via `pytest.ini`
2. **Missing Dependencies**: Run `poetry install --with dev`
3. **Permission Errors**: Check file permissions on scripts
4. **Network Timeouts**: Increase timeout values in test configuration

### Debug Mode

```bash
# Verbose test output
pytest -v -s tests/test_environment.py

# Debug dashboard with full diagnostics
python tools/debug_dashboard.py
# Choose option 5 for full diagnostics
```

### Performance Issues

```bash
# Identify slow components
python tests/test_performance.py

# Monitor resource usage
python tools/monitoring_setup.py collect
```

## Framework Architecture

### Test Organization

```
tests/
├── test_environment.py       # Environment validation
├── test_connectivity.py      # External API connectivity
├── test_infrastructure.py    # Cloud infrastructure
├── test_jarvys_dev.py        # JARVYS_DEV core tests
├── test_jarvys_ai.py         # JARVYS_AI core tests
├── test_agent_communication.py # Inter-agent communication
├── test_workflows.py         # GitHub Actions workflows
├── test_automation.py        # Automation and scheduling
├── test_deployment.py        # Deployment processes
├── test_api_integration.py   # API endpoint testing
└── test_performance.py       # Performance benchmarks
```

### Tool Organization

```
tools/
├── debug_dashboard.py        # Interactive debugging
├── health_check.py          # System health monitoring
├── log_analyzer.py          # Log analysis and patterns
├── error_tracker.py         # Error detection and tracking
└── monitoring_setup.py      # Monitoring system setup
```

### Data Flow

1. **Tests** validate functionality and catch regressions
2. **Health Checks** monitor system status continuously
3. **Error Tracker** identifies issues in real-time
4. **Log Analyzer** processes historical data
5. **Monitoring** collects metrics and trends
6. **Debug Dashboard** provides unified interface

## Best Practices

### Test Development

1. **Graceful Degradation**: Tests should skip when dependencies unavailable
2. **Clear Naming**: Use descriptive test function names
3. **Isolation**: Tests should not depend on external state
4. **Cleanup**: Remove temporary files and test data

### Error Handling

1. **Categorization**: Use appropriate severity levels
2. **Context**: Provide sufficient context for debugging
3. **Actionability**: Include suggested fixes
4. **Non-blocking**: Don't crash on individual test failures

### Performance

1. **Baseline**: Establish performance baselines
2. **Regression**: Monitor for performance regressions
3. **Optimization**: Identify bottlenecks systematically
4. **Monitoring**: Track performance trends over time

## Contributing

### Adding New Tests

1. Follow existing test patterns
2. Use appropriate pytest markers
3. Handle missing dependencies gracefully
4. Add documentation for complex test cases

### Extending Tools

1. Maintain consistent CLI interfaces
2. Use JSON for machine-readable output
3. Provide human-readable summaries
4. Handle errors gracefully

### Reporting Issues

1. Use error tracker to identify patterns
2. Include debugging output
3. Provide reproduction steps
4. Check existing documentation

## Support

For issues and questions:

1. Run `python tools/debug_dashboard.py` for comprehensive diagnostics
2. Check error patterns with `python tools/error_tracker.py`
3. Review logs with `python tools/log_analyzer.py`
4. Verify system health with `python tools/health_check.py`

The framework is designed to be self-diagnostic and should provide clear guidance on resolving most issues automatically.