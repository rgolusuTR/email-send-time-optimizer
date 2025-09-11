#!/usr/bin/env python3
"""
Test script for the prompt parser functionality
"""

from prompt_parser import PromptParser

def test_prompt_parsing():
    """Test various prompt parsing scenarios"""
    parser = PromptParser()
    
    test_cases = [
        {
            "prompt": "Create a new page called 'Test Page', add an Article Paragraph component, and fill it with 'Hello World'",
            "description": "Complete workflow with page creation, component addition, and content"
        },
        {
            "prompt": "Make a page named 'News Article' under the news folder",
            "description": "Page creation with specific folder location"
        },
        {
            "prompt": "Add a Hero Banner component and update it with 'Welcome to our site'",
            "description": "Component addition with content update"
        },
        {
            "prompt": "Create a page called 'Contact Us', add a title component, and write 'Get in touch with us'",
            "description": "Multiple actions in sequence"
        },
        {
            "prompt": "Fill the component with 'This is test content for the automation'",
            "description": "Content update only"
        }
    ]
    
    print("🧪 Testing AEM Prompt Parser")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Prompt: '{test_case['prompt']}'")
        print("-" * 30)
        
        try:
            # Parse the prompt
            parsed = parser.parse_prompt(test_case['prompt'])
            
            # Generate execution plan
            plan = parser.generate_execution_plan(parsed)
            
            print(f"✅ Parsed successfully!")
            print(f"Page Name: {parsed.page_name}")
            print(f"Page Title: {parsed.page_title}")
            print(f"Target Path: {parsed.target_path}")
            print(f"Actions: {len(parsed.actions)}")
            
            for j, action in enumerate(parsed.actions, 1):
                print(f"  {j}. {action.action_type}: {action.parameters}")
            
            print("\nExecution Plan:")
            for step in plan:
                print(f"  {step}")
                
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
        
        print()

def test_component_mapping():
    """Test component name mapping"""
    parser = PromptParser()
    
    print("🧩 Testing Component Mapping")
    print("=" * 30)
    
    test_components = [
        "paragraph",
        "article paragraph", 
        "text",
        "hero",
        "banner",
        "image",
        "title",
        "heading"
    ]
    
    for component in test_components:
        mapped = parser.component_mappings.get(component, "Article Paragraph")
        print(f"'{component}' → '{mapped}'")

if __name__ == "__main__":
    test_prompt_parsing()
    print("\n" + "=" * 50)
    test_component_mapping()
    
    print("\n🎉 Parser testing completed!")
    print("\nTo test the full agent, run:")
    print("  python aem_agent.py")
    print("\nTo use the interactive CLI:")
    print("  python cli.py")
