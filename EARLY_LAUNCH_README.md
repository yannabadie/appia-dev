# 🚀 Early Launch Issues Setup Automation

## Overview

The Early Launch Issues Setup Automation is designed to activate immediate automated processing of the repository's backlog of 10+ open issues. This system enables autonomous issue handling with priority-based processing and continuous monitoring.

## Features

### 🎯 Priority-Based Issue Processing
- **High Priority Autonomy Issues** (#44, #45): Intelligence Adaptative and Apprentissage Continu
- **Epic Issues** (#2, #3, #5, #6, #7): Bootstrap infrastructure, Core tools, Persona & données  
- **Automated Tasks** (#41, #42): Model detection and automated workflows

### ⚙️ Automation Components

#### 1. Early Launch Workflow (`.github/workflows/early-launch-issues.yml`)
- **Trigger**: Manual dispatch, 30-minute schedule, push events
- **Jobs**:
  - `trigger-jarvys-autonomous`: Activates JARVYS Cloud Deployment in autonomous mode
  - `process-issue-backlog`: Processes priority issues with automated labeling
  - `monitor-early-launch`: Generates status reports and monitors progress
  - `notification`: Sends status notifications

#### 2. Issue Processor Script (`scripts/issue_processor.py`)
- **Priority-based processing**: Sorts issues by importance and category
- **Automated labeling**: Adds appropriate labels based on issue type
- **Progress tracking**: Adds comments to issues with processing status
- **Dashboard integration**: Updates Supabase dashboard with progress
- **Status reporting**: Generates comprehensive status reports

## Usage

### Manual Trigger
```bash
# Trigger via GitHub Actions UI with mode options:
# - process_backlog: Full issue processing cycle
# - priority_check: Check priority issues only  
# - monitor_status: Generate status report
```

### Automatic Schedule
- Runs every **30 minutes** automatically
- Processes up to 5 priority issues per cycle
- Updates dashboard and generates reports

### CLI Usage
```bash
# Process priority issues
poetry run python scripts/issue_processor.py --mode priority

# Update dashboard
poetry run python scripts/issue_processor.py --mode dashboard_update

# Generate status report
poetry run python scripts/issue_processor.py --mode status_report
```

## Configuration

### Environment Variables
```bash
GH_TOKEN=<github_token>           # Required for GitHub API access
GH_REPO=yannabadie/appia-dev      # Repository name
SUPABASE_URL=<supabase_url>       # Supabase dashboard URL
SUPABASE_KEY=<supabase_key>       # Supabase API key
OPENAI_API_KEY=<openai_key>       # OpenAI API key
```

### Priority Mapping
The system uses a predefined priority mapping in `issue_processor.py`:

```python
PRIORITY_ISSUES = {
    # High Priority Autonomy (Priority 1)
    44: {"priority": 1, "category": "autonomy", "title": "Intelligence Adaptative"},
    45: {"priority": 1, "category": "autonomy", "title": "Apprentissage Continu"},
    
    # Bootstrap Infrastructure (Priority 2)
    1, 2, 5: {"priority": 2, "category": "epic", "title": "Bootstrap infrastructure"},
    
    # Core Tools (Priority 3)
    3, 6: {"priority": 3, "category": "epic", "title": "Core tools"},
    
    # Persona & Données (Priority 4)
    4, 7: {"priority": 4, "category": "epic", "title": "Persona & données"},
    
    # Automation (Priority 5)
    41, 42: {"priority": 5, "category": "automation", "title": "Automated tasks"}
}
```

## Integration

### Supabase Dashboard
- **URL**: https://kzcswopokvknxmxczilu.supabase.co
- **Tables**: 
  - `jarvys_issue_processing`: Logs issue processing events
  - `jarvys_dashboard_status`: Stores current status information

### JARVYS Cloud Deployment
- Automatically triggers the main JARVYS workflow in autonomous mode
- Integrates with existing deployment scripts
- Uses all configured GitHub Actions secrets

## Success Criteria

- [x] Early launch workflow successfully triggers
- [x] Issues are processed in priority order
- [x] Automation reports progress to dashboard
- [x] No manual intervention required for standard issue processing  
- [x] 30-minute autonomous cycle is active and functional

## Monitoring

### Status Report Example
```
🚀 EARLY LAUNCH STATUS REPORT
============================================================
📅 Generated: 2025-07-11T18:37:07Z
📋 Total Open Issues: 12
⭐ Priority Issues: 10
🔄 Next Cycle: 30 minutes

📊 Issues by Category:
   autonomy: 2
   epic: 6
   automation: 2

🎯 Next Priority Issues:
   #44: Intelligence Adaptative (Priority: 1)
   #45: Apprentissage Continu (Priority: 1)
   #2: Bootstrap infrastructure (Priority: 2)
============================================================
```

### Dashboard Metrics
- Total open issues count
- Priority issues processed
- Last update timestamp
- Early launch status
- Next cycle timing

## Testing

Run the test suite to validate functionality:

```bash
poetry run pytest tests/test_early_launch.py -v
```

Test coverage includes:
- Issue processor initialization
- Priority mapping validation
- Issue prioritization logic
- Status report generation
- Workflow file validation
- Success criteria verification

## Files Modified/Created

### New Files
- `.github/workflows/early-launch-issues.yml` - Main automation workflow
- `scripts/issue_processor.py` - Issue processing script
- `tests/test_early_launch.py` - Test suite for early launch functionality
- `EARLY_LAUNCH_README.md` - This documentation

### Dependencies
- Uses existing `pyproject.toml` dependencies
- Requires: `PyGithub`, `supabase`, `requests`
- Compatible with existing Poetry setup

## Next Steps

1. **Activation**: The early launch system is ready for immediate activation
2. **Monitoring**: Watch the first few cycles for proper operation
3. **Adjustment**: Fine-tune priority mappings based on results
4. **Scaling**: Expand to handle more issues per cycle if needed

## Support

For issues or questions about the early launch system:
1. Check the GitHub Actions logs for workflow execution details
2. Review issue comments for processing status
3. Monitor the Supabase dashboard for real-time metrics
4. Run status reports manually for diagnostic information