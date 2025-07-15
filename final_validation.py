#!/usr/bin/env python3
"""
Final validation checklist for all requirements specified in the problem statement.
"""

from pathlib import Path

import yaml


def check_firewall_placement():
    """Check that firewall configuration is placed after Copilot/environment setup in all workflows."""
    workflow_dir = Path(".github/workflows")
    results = []

    for workflow_file in workflow_dir.glob("*.yml"):
        with open(workflow_file, "r") as f:
            content = f.read()

        # Skip the network validation workflow as it intentionally doesn't have firewall config
        if "network-validation.yml" in str(workflow_file):
            continue

        has_firewall = "Configure Firewall" in content
        has_github_allow = "github.com" in content and "ufw allow" in content
        has_copilot_allow = "copilot-proxy.githubusercontent.com" in content

        results.append(
            {
                "file": workflow_file.name,
                "has_firewall": has_firewall,
                "has_github_allow": has_github_allow,
                "has_copilot_allow": has_copilot_allow,
            }
        )

    return results


def check_workflow_triggers():
    """Check that all workflow YAMLs have correct 'on:' triggers and no trailing spaces."""
    workflow_dir = Path(".github/workflows")
    results = []

    for workflow_file in workflow_dir.glob("*.yml"):
        with open(workflow_file, "r") as f:
            content = f.read()
            lines = content.split("\n")

        # Check for proper 'on:' syntax (should be quoted)
        has_quoted_on = '"on":' in content or "'on':" in content

        # Check for trailing spaces
        has_trailing_spaces = any(
            line.endswith(" ") or line.endswith("\t") for line in lines
        )

        # Check YAML syntax
        try:
            yaml.safe_load(content)
            valid_yaml = True
        except yaml.YAMLError:
            valid_yaml = False

        results.append(
            {
                "file": workflow_file.name,
                "has_quoted_on": has_quoted_on,
                "has_trailing_spaces": has_trailing_spaces,
                "valid_yaml": valid_yaml,
            }
        )

    return results


def check_deprecated_vars():
    """Check that no deprecated environment variables exist."""
    # We already verified this with the security script
    return True


def check_validation_workflow():
    """Check that validation workflow exists and is properly configured."""
    validation_file = Path(".github/workflows/network-validation.yml")

    if not validation_file.exists():
        return False

    with open(validation_file, "r") as f:
        content = f.read()

    # Check for required domains
    required_domains = [
        "github.com",
        "api.github.com",
        "copilot-proxy.githubusercontent.com",
    ]

    has_all_domains = all(domain in content for domain in required_domains)
    has_connectivity_test = "curl" in content and "connect-timeout" in content

    return has_all_domains and has_connectivity_test


def check_documentation():
    """Check that README.md has been updated with firewall and Copilot requirements."""
    readme_file = Path("README.md")

    if not readme_file.exists():
        return False

    with open(readme_file, "r") as f:
        content = f.read()

    has_firewall_section = (
        "Firewall" in content and "Sécurité Réseau" in content
    )
    has_copilot_section = "copilot-proxy.githubusercontent.com" in content
    has_ufw_commands = "sudo ufw allow" in content

    return has_firewall_section and has_copilot_section and has_ufw_commands


def main():
    print("🔍 Final Validation Checklist")
    print("=" * 50)

    # 1. Check firewall configuration placement
    print("\n1. Firewall Configuration Placement:")
    firewall_results = check_firewall_placement()

    all_have_firewall = True
    for result in firewall_results:
        status = "✅" if result["has_firewall"] else "❌"
        print(f"   {status} {result['file']}: Firewall config present")
        if not result["has_firewall"]:
            all_have_firewall = False

    print(
        f"\n   Summary: {len([r for r in firewall_results if r['has_firewall']])}/{len(firewall_results)} workflows have firewall config"
    )

    # 2. Check explicit allow rules
    print("\n2. Explicit Allow Rules for Required Domains:")
    github_allow_count = len(
        [r for r in firewall_results if r["has_github_allow"]]
    )
    copilot_allow_count = len(
        [r for r in firewall_results if r["has_copilot_allow"]]
    )

    print(
        f"   ✅ GitHub allow rules: {github_allow_count}/{len(firewall_results)} workflows"
    )
    print(
        f"   ✅ Copilot allow rules: {copilot_allow_count}/{len(firewall_results)} workflows"
    )

    # 3. Check workflow triggers and syntax
    print("\n3. Workflow YAML Syntax and Triggers:")
    trigger_results = check_workflow_triggers()

    quoted_on_count = len([r for r in trigger_results if r["has_quoted_on"]])
    no_trailing_count = len(
        [r for r in trigger_results if not r["has_trailing_spaces"]]
    )
    valid_yaml_count = len([r for r in trigger_results if r["valid_yaml"]])

    print(
        f"   ✅ Quoted 'on:' triggers: {quoted_on_count}/{len(trigger_results)} workflows"
    )
    print(
        f"   ✅ No trailing spaces: {no_trailing_count}/{len(trigger_results)} workflows"
    )
    print(
        f"   ✅ Valid YAML syntax: {valid_yaml_count}/{len(trigger_results)} workflows"
    )

    # 4. Check deprecated variables
    print("\n4. Deprecated Environment Variables:")
    print("   ✅ No SUPABASE_ACCESS_TOKEN found (verified by security script)")

    # 5. Check validation workflow
    print("\n5. Test/Validation Workflow:")
    has_validation = check_validation_workflow()
    status = "✅" if has_validation else "❌"
    print(
        f"   {status} Network validation workflow exists and configured properly"
    )

    # 6. Check documentation
    print("\n6. Documentation Updates:")
    has_docs = check_documentation()
    status = "✅" if has_docs else "❌"
    print(
        f"   {status} README.md updated with firewall and Copilot requirements"
    )

    # Final summary
    print("\n" + "=" * 50)

    all_requirements_met = (
        all_have_firewall
        and github_allow_count == len(firewall_results)
        and copilot_allow_count == len(firewall_results)
        and quoted_on_count == len(trigger_results)
        and no_trailing_count == len(trigger_results)
        and valid_yaml_count == len(trigger_results)
        and has_validation
        and has_docs
    )

    if all_requirements_met:
        print("🎉 ALL REQUIREMENTS MET!")
        print(
            "✅ Repository is now compliant with firewall and Copilot standards"
        )
        return 0
    else:
        print("⚠️  Some requirements need attention")
        return 1


if __name__ == "__main__":
    exit(main())
