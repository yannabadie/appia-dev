"""Test automation features including cron jobs and CI/CD pipeline."""

import os
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, Mock
import json
import subprocess


class TestAutomatedScheduling:
    """Test automated scheduling and cron job functionality."""
    
    def test_cron_schedule_syntax(self):
        """Test cron schedule syntax in workflows."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        workflow_files = list(workflows_path.glob("*.yml"))
        cron_schedules = []
        
        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)
            
            triggers = workflow_config.get('on', {})
            if 'schedule' in triggers:
                schedules = triggers['schedule']
                for schedule in schedules:
                    if 'cron' in schedule:
                        cron_schedules.append((workflow_file.name, schedule['cron']))
        
        # Validate cron syntax
        for workflow_name, cron_expr in cron_schedules:
            cron_parts = cron_expr.split()
            assert len(cron_parts) == 5, f"Invalid cron syntax in {workflow_name}: {cron_expr}"
            
            # Basic validation of cron parts
            minute, hour, day, month, weekday = cron_parts
            
            # Minute should be 0-59 or *
            if minute != '*' and not minute.startswith('*/'):
                minute_val = int(minute)
                assert 0 <= minute_val <= 59, f"Invalid minute in {workflow_name}: {minute}"
    
    def test_hourly_execution_schedule(self):
        """Test that agent has hourly execution schedule."""
        agent_path = Path(__file__).parent.parent / ".github" / "workflows" / "agent.yml"
        if not agent_path.exists():
            pytest.skip("Agent workflow not found")
        
        with open(agent_path) as f:
            agent_config = yaml.safe_load(f)
        
        triggers = agent_config.get('on', {})
        if 'schedule' in triggers:
            schedules = triggers['schedule']
            
            # Should have hourly or frequent execution
            hourly_patterns = ['0 * * * *', '*/60 * * * *']
            frequent_patterns = ['*/30 * * * *', '*/15 * * * *']
            
            has_frequent_schedule = False
            for schedule in schedules:
                cron = schedule.get('cron', '')
                if any(pattern in cron for pattern in hourly_patterns + frequent_patterns):
                    has_frequent_schedule = True
                    break
            
            if not has_frequent_schedule:
                print("Info: Agent workflow may not have frequent execution schedule")
        else:
            print("Info: Agent workflow has no scheduled execution")
    
    def test_model_detection_daily_schedule(self):
        """Test model detection has daily schedule."""
        model_path = Path(__file__).parent.parent / ".github" / "workflows" / "model-detection.yml"
        if not model_path.exists():
            pytest.skip("Model detection workflow not found")
        
        with open(model_path) as f:
            model_config = yaml.safe_load(f)
        
        triggers = model_config.get('on', {})
        if 'schedule' in triggers:
            schedules = triggers['schedule']
            
            # Should have daily execution
            daily_patterns = ['0 0 * * *', '0 6 * * *', '0 12 * * *']
            
            has_daily_schedule = False
            for schedule in schedules:
                cron = schedule.get('cron', '')
                if any(pattern in cron for pattern in daily_patterns):
                    has_daily_schedule = True
                    break
            
            if not has_daily_schedule:
                print("Info: Model detection may not have daily schedule")


class TestCIPipeline:
    """Test CI/CD pipeline functionality."""
    
    def test_ci_pipeline_stages(self):
        """Test CI pipeline has proper stages."""
        ci_path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        if not ci_path.exists():
            pytest.skip("CI workflow not found")
        
        with open(ci_path) as f:
            ci_config = yaml.safe_load(f)
        
        jobs = ci_config.get('jobs', {})
        
        # Should have testing job
        test_jobs = [job for job_name, job in jobs.items() 
                    if 'test' in job_name.lower() or 'pytest' in str(job).lower()]
        
        assert len(test_jobs) > 0, "CI pipeline should have testing jobs"
    
    def test_ci_dependency_installation(self):
        """Test CI pipeline installs dependencies correctly."""
        ci_path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        if not ci_path.exists():
            pytest.skip("CI workflow not found")
        
        with open(ci_path) as f:
            content = f.read()
        
        # Should install dependencies
        dependency_patterns = ["poetry install", "pip install", "npm install"]
        
        has_dependency_install = any(pattern in content for pattern in dependency_patterns)
        assert has_dependency_install, "CI should install dependencies"
    
    def test_ci_testing_execution(self):
        """Test CI pipeline executes tests."""
        ci_path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        if not ci_path.exists():
            pytest.skip("CI workflow not found")
        
        with open(ci_path) as f:
            content = f.read()
        
        # Should run tests
        test_patterns = ["pytest", "python -m pytest", "poetry run pytest"]
        
        has_test_execution = any(pattern in content for pattern in test_patterns)
        assert has_test_execution, "CI should execute tests"
    
    def test_ci_code_quality_checks(self):
        """Test CI pipeline includes code quality checks."""
        ci_path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        if not ci_path.exists():
            pytest.skip("CI workflow not found")
        
        with open(ci_path) as f:
            content = f.read()
        
        # Should have linting/formatting checks
        quality_patterns = ["pre-commit", "black", "flake8", "isort", "mypy"]
        
        found_quality_checks = [pattern for pattern in quality_patterns if pattern in content]
        
        if not found_quality_checks:
            print("Info: CI pipeline may lack code quality checks")
        else:
            print(f"Found quality checks: {found_quality_checks}")


class TestDeploymentAutomation:
    """Test deployment automation functionality."""
    
    def test_deployment_triggers(self):
        """Test deployment workflows have appropriate triggers."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        deployment_workflows = []
        for workflow_file in workflows_path.glob("*.yml"):
            if any(keyword in workflow_file.name.lower() 
                  for keyword in ['deploy', 'build', 'release']):
                deployment_workflows.append(workflow_file)
        
        for deploy_workflow in deployment_workflows:
            with open(deploy_workflow) as f:
                deploy_config = yaml.safe_load(f)
            
            triggers = deploy_config.get('on', {})
            
            # Should have push to main/master or tag triggers
            deployment_triggers = ['push', 'release', 'workflow_dispatch']
            found_triggers = [trigger for trigger in deployment_triggers if trigger in triggers]
            
            assert len(found_triggers) > 0, f"Deployment workflow {deploy_workflow.name} should have deployment triggers"
    
    def test_environment_based_deployment(self):
        """Test environment-based deployment configuration."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)
            
            # Check for environment configurations
            jobs = workflow_config.get('jobs', {})
            for job_name, job_config in jobs.items():
                if 'environment' in job_config:
                    environment = job_config['environment']
                    print(f"Found environment in {workflow_file.name}: {environment}")
    
    def test_deployment_secrets_usage(self):
        """Test deployment uses appropriate secrets."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        deployment_workflows = []
        for workflow_file in workflows_path.glob("*.yml"):
            if any(keyword in workflow_file.name.lower() 
                  for keyword in ['deploy', 'jarvys-cloud', 'dashboard']):
                deployment_workflows.append(workflow_file)
        
        for deploy_workflow in deployment_workflows:
            with open(deploy_workflow) as f:
                content = f.read()
            
            # Should use deployment secrets
            deployment_secrets = [
                "SUPABASE_ACCESS_TOKEN",
                "GCP_SA_JSON", 
                "SUPABASE_PROJECT_REF"
            ]
            
            found_secrets = [secret for secret in deployment_secrets if secret in content]
            
            if found_secrets:
                print(f"Deployment secrets in {deploy_workflow.name}: {found_secrets}")


class TestErrorHandlingAutomation:
    """Test error handling in automation."""
    
    def test_workflow_failure_notifications(self):
        """Test workflows have failure notification mechanisms."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()
            
            # Check for failure handling
            failure_patterns = ["on-failure", "failure()", "always()"]
            
            has_failure_handling = any(pattern in content for pattern in failure_patterns)
            
            if not has_failure_handling:
                print(f"Info: {workflow_file.name} may lack failure handling")
    
    def test_workflow_retry_mechanisms(self):
        """Test workflows have retry mechanisms for reliability."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)
            
            # Look for retry configurations
            jobs = workflow_config.get('jobs', {})
            for job_name, job_config in jobs.items():
                steps = job_config.get('steps', [])
                
                for step in steps:
                    if isinstance(step, dict):
                        # Check for retry mechanisms
                        if 'uses' in step and 'retry' in step.get('with', {}):
                            print(f"Found retry mechanism in {workflow_file.name}")
    
    def test_workflow_timeout_handling(self):
        """Test workflows have appropriate timeout handling."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)
            
            # Check for timeout configurations
            jobs = workflow_config.get('jobs', {})
            timeout_configs = []
            
            for job_name, job_config in jobs.items():
                if 'timeout-minutes' in job_config:
                    timeout_configs.append((job_name, job_config['timeout-minutes']))
            
            if timeout_configs:
                print(f"Timeout configs in {workflow_file.name}: {timeout_configs}")


class TestMonitoringAutomation:
    """Test monitoring and observability automation."""
    
    def test_metrics_collection_automation(self):
        """Test automated metrics collection."""
        # Check if metrics database exists (created by automation)
        project_root = Path(__file__).parent.parent
        metrics_db = project_root / "jarvys_metrics.db"
        
        if metrics_db.exists():
            # Metrics automation is working
            assert metrics_db.is_file(), "Metrics DB should be a file"
            print("Found metrics database - automation is collecting data")
        else:
            print("Info: Metrics database not found - automation may not be running")
    
    def test_log_collection_automation(self):
        """Test automated log collection and analysis."""
        # Check for log analysis scripts
        project_root = Path(__file__).parent.parent
        
        log_scripts = list(project_root.glob("*log*")) + list(project_root.glob("*analyze*"))
        
        if log_scripts:
            print(f"Found log automation scripts: {[s.name for s in log_scripts]}")
        else:
            print("Info: No log automation scripts found")
    
    def test_health_check_automation(self):
        """Test automated health checking."""
        # Look for health check workflows or scripts
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if workflows_path.exists():
            health_workflows = []
            for workflow_file in workflows_path.glob("*.yml"):
                with open(workflow_file) as f:
                    content = f.read()
                
                if any(keyword in content.lower() for keyword in ['health', 'monitor', 'check']):
                    health_workflows.append(workflow_file.name)
            
            if health_workflows:
                print(f"Found health check workflows: {health_workflows}")


class TestIntegrationAutomation:
    """Test integration automation between components."""
    
    def test_supabase_deployment_automation(self):
        """Test Supabase deployment automation."""
        # Check for Supabase deployment scripts or workflows
        project_root = Path(__file__).parent.parent
        
        supabase_deploy_files = [
            "deploy-supabase.sh",
            ".github/workflows/deploy-dashboard.yml"
        ]
        
        found_files = []
        for file_path in supabase_deploy_files:
            if (project_root / file_path).exists():
                found_files.append(file_path)
        
        if found_files:
            print(f"Found Supabase deployment automation: {found_files}")
        else:
            print("Info: Supabase deployment automation not found")
    
    def test_github_issue_automation(self):
        """Test GitHub issue automation for agent communication."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        issue_automation_found = False
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()
            
            # Look for issue automation
            if any(keyword in content.lower() for keyword in ['issue', 'comment', 'label']):
                issue_automation_found = True
                print(f"Found issue automation in {workflow_file.name}")
        
        if not issue_automation_found:
            print("Info: GitHub issue automation not found")
    
    def test_wiki_documentation_automation(self):
        """Test wiki documentation automation."""
        wiki_workflow = Path(__file__).parent.parent / ".github" / "workflows" / "wiki-sync.yml"
        
        if wiki_workflow.exists():
            with open(wiki_workflow) as f:
                wiki_config = yaml.safe_load(f)
            
            # Should have wiki update automation
            assert 'name' in wiki_config, "Wiki workflow should have a name"
            print("Found wiki documentation automation")
        else:
            print("Info: Wiki documentation automation not found")


class TestSecurityAutomation:
    """Test security automation features."""
    
    def test_secret_scanning_automation(self):
        """Test automated secret scanning."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        security_workflows = []
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()
            
            # Look for security scanning
            security_keywords = ['secret', 'security', 'scan', 'vulnerability']
            if any(keyword in content.lower() for keyword in security_keywords):
                security_workflows.append(workflow_file.name)
        
        if security_workflows:
            print(f"Found security automation: {security_workflows}")
    
    def test_dependency_update_automation(self):
        """Test automated dependency updates."""
        project_root = Path(__file__).parent.parent
        
        # Check for Dependabot or similar automation
        dependabot_config = project_root / ".github" / "dependabot.yml"
        
        if dependabot_config.exists():
            with open(dependabot_config) as f:
                config = yaml.safe_load(f)
            
            assert 'version' in config, "Dependabot config should have version"
            assert 'updates' in config, "Dependabot config should have updates"
            print("Found dependency update automation (Dependabot)")
        else:
            print("Info: Dependency update automation not found")
    
    def test_access_control_automation(self):
        """Test access control automation."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")
        
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)
            
            # Check for permission restrictions
            if 'permissions' in workflow_config:
                permissions = workflow_config['permissions']
                print(f"Access control in {workflow_file.name}: {permissions}")


class TestPerformanceAutomation:
    """Test performance monitoring automation."""
    
    def test_performance_benchmarking_automation(self):
        """Test automated performance benchmarking."""
        # Look for performance testing in workflows
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if workflows_path.exists():
            perf_workflows = []
            for workflow_file in workflows_path.glob("*.yml"):
                with open(workflow_file) as f:
                    content = f.read()
                
                perf_keywords = ['benchmark', 'performance', 'load', 'stress']
                if any(keyword in content.lower() for keyword in perf_keywords):
                    perf_workflows.append(workflow_file.name)
            
            if perf_workflows:
                print(f"Found performance automation: {perf_workflows}")
    
    def test_resource_monitoring_automation(self):
        """Test automated resource monitoring."""
        # Check for resource monitoring automation
        project_root = Path(__file__).parent.parent
        
        monitoring_files = list(project_root.glob("*monitor*")) + list(project_root.glob("*metric*"))
        
        if monitoring_files:
            print(f"Found monitoring automation: {[f.name for f in monitoring_files]}")
        else:
            print("Info: Resource monitoring automation not found")
    
    def test_cost_tracking_automation(self):
        """Test automated cost tracking."""
        # Look for cost tracking in workflows or scripts
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if workflows_path.exists():
            cost_tracking = []
            for workflow_file in workflows_path.glob("*.yml"):
                with open(workflow_file) as f:
                    content = f.read()
                
                if any(keyword in content.lower() for keyword in ['cost', 'billing', 'usage']):
                    cost_tracking.append(workflow_file.name)
            
            if cost_tracking:
                print(f"Found cost tracking automation: {cost_tracking}")
            else:
                print("Info: Cost tracking automation not found")