#!/usr/bin/env python3
"""
Test Script for Enhanced JARVYS Prompt System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_system_prompts import EnhancedPromptSystem

def test_enhanced_prompts():
    """Test the enhanced prompt system"""
    print("🧪 Testing Enhanced JARVYS Prompt System")
    print("=" * 50)
    
    # Initialize prompt system
    enhanced_prompts = EnhancedPromptSystem()
    
    # Mock memory retriever
    def mock_memory_retriever(memory_type=None, limit=10):
        return [
            {
                "content": "Previous successful code generation for file processing",
                "importance_score": 0.8,
                "timestamp": "2025-07-17 10:30:00"
            },
            {
                "content": "Error handling pattern for API integrations", 
                "importance_score": 0.9,
                "timestamp": "2025-07-17 09:15:00"
            }
        ]
    
    enhanced_prompts.memory_retriever = mock_memory_retriever
    enhanced_prompts.environment_info = {
        'secrets_summary': {
            'github': True,
            'supabase': True, 
            'xai_grok': True,
            'claude': True,
            'gcp': False
        }
    }
    
    print("✅ Enhanced prompt system initialized")
    print()
    
    # Test 1: Grok orchestrator prompt
    print("🤖 Test 1: Grok Orchestrator Prompt")
    print("-" * 40)
    
    grok_prompt = enhanced_prompts.get_grok_orchestrator_prompt(
        task="Create a file processing system with error handling",
        agent_type="DEV",
        repo_context={"current_repo": "appia-dev", "task_context": "file_processing"},
        collaboration_mode=True
    )
    
    print("📝 Grok Prompt Preview (first 500 chars):")
    print(grok_prompt[:500] + "...\n")
    
    # Test 2: Claude validation prompt
    print("🔍 Test 2: Claude Validation Prompt")
    print("-" * 40)
    
    sample_code = '''
def process_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    return content.upper()
'''
    
    claude_prompt = enhanced_prompts.get_claude_validation_prompt(
        code=sample_code,
        task_description="File processing with error handling",
        grok_metadata={"generation_confidence": 0.8}
    )
    
    print("📝 Claude Prompt Preview (first 500 chars):")
    print(claude_prompt[:500] + "...\n")
    
    # Test 3: Adaptive prompt
    print("🎯 Test 3: Adaptive Prompt")
    print("-" * 40)
    
    adaptive_prompt = enhanced_prompts.get_adaptive_prompt(
        context_type="error_recovery",
        current_state={"status": "error_detected", "phase": "code_generation", "metrics": "low_success_rate"},
        learning_data={"success_rate": 0.4}
    )
    
    print("📝 Adaptive Prompt Preview (first 500 chars):")
    print(adaptive_prompt[:500] + "...\n")
    
    print("✅ All prompt tests completed successfully!")
    print("🚀 Enhanced prompt system is ready for integration")

if __name__ == "__main__":
    test_enhanced_prompts()
