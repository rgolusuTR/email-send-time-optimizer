#!/usr/bin/env python3
"""
AEM Automation Agent CLI
Command-line interface for the AEM automation agent
"""

import asyncio
import argparse
import sys
from loguru import logger
from aem_agent import AEMAgent
from config import settings

class AEMAgentCLI:
    """Command-line interface for the AEM Agent"""
    
    def __init__(self):
        self.agent = AEMAgent()
    
    async def run_interactive_mode(self):
        """Run the agent in interactive mode"""
        print("🤖 AEM Automation Agent - Interactive Mode")
        print("Type 'help' for available commands, 'quit' to exit")
        print("-" * 50)
        
        # Initialize agent
        await self.agent.start()
        
        # Login
        login_success = await self._handle_login()
        if not login_success:
            print("❌ Login failed. Exiting...")
            await self.agent.stop()
            return
        
        print("✅ Successfully logged in to AEM!")
        print("\nYou can now give me natural language instructions like:")
        print("  • 'Create a new page called Test Page'")
        print("  • 'Add an Article Paragraph component and fill it with Hello World'")
        print("  • 'Create a page called News Article, add a title component'")
        print()
        
        # Interactive loop
        while True:
            try:
                user_input = input("🎯 Enter your instruction: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'screenshot':
                    await self.agent.take_screenshot()
                    print("📸 Screenshot saved!")
                    continue
                elif user_input.lower() == 'preview':
                    await self.agent.preview_page()
                    print("👀 Page preview opened!")
                    continue
                elif not user_input:
                    continue
                
                # Execute the prompt
                print(f"\n🔄 Processing: {user_input}")
                result = await self.agent.execute_prompt(user_input)
                
                if result["success"]:
                    print("✅ Task completed successfully!")
                    print("\n📋 Actions performed:")
                    for action in result["actions_completed"]:
                        print(f"  ✓ {action}")
                else:
                    print(f"❌ Task failed: {result['error']}")
                    if result["actions_completed"]:
                        print("\n📋 Actions completed before failure:")
                        for action in result["actions_completed"]:
                            print(f"  ✓ {action}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Cleanup
        await self.agent.stop()
        print("🔚 Agent stopped. Goodbye!")
    
    async def run_single_command(self, prompt: str):
        """Run a single command and exit"""
        try:
            # Initialize agent
            await self.agent.start()
            
            # Login
            login_success = await self._handle_login()
            if not login_success:
                print("❌ Login failed.")
                return False
            
            print(f"🔄 Executing: {prompt}")
            
            # Execute the prompt
            result = await self.agent.execute_prompt(prompt)
            
            if result["success"]:
                print("✅ Task completed successfully!")
                print("\n📋 Actions performed:")
                for action in result["actions_completed"]:
                    print(f"  ✓ {action}")
                return True
            else:
                print(f"❌ Task failed: {result['error']}")
                if result["actions_completed"]:
                    print("\n📋 Actions completed before failure:")
                    for action in result["actions_completed"]:
                        print(f"  ✓ {action}")
                return False
        
        finally:
            await self.agent.stop()
    
    async def _handle_login(self) -> bool:
        """Handle the login process"""
        if settings.aem_username and settings.aem_password:
            print("🔐 Logging in with credentials from .env file...")
            return await self.agent.login()
        else:
            print("🔐 Please enter your AEM credentials:")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            
            if not username or not password:
                print("❌ Username and password are required")
                return False
            
            return await self.agent.login(username, password)
    
    def _show_help(self):
        """Show help information"""
        print("\n📚 AEM Automation Agent Help")
        print("=" * 40)
        print("Available commands:")
        print("  help       - Show this help message")
        print("  screenshot - Take a screenshot of current page")
        print("  preview    - Open page preview")
        print("  quit/exit  - Exit the application")
        print()
        print("Natural language instructions you can use:")
        print("  • Create a new page called 'Page Name'")
        print("  • Add an Article Paragraph component")
        print("  • Fill the component with 'Your content here'")
        print("  • Create a page called 'News', add a title component, and fill it with 'Breaking News'")
        print()
        print("The agent will automatically:")
        print("  • Navigate to the correct location in AEM")
        print("  • Create pages with appropriate templates")
        print("  • Add and configure components")
        print("  • Update content as requested")
        print()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AEM Automation Agent - Automate AEM page authoring with natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s -c "Create a page called Test"     # Single command
  %(prog)s --interactive                      # Explicit interactive mode
        """
    )
    
    parser.add_argument(
        '-c', '--command',
        help='Execute a single command and exit'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode (default if no command specified)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.add(sys.stdout, level="DEBUG")
    else:
        logger.add(sys.stdout, level="INFO")
    
    # Override headless setting if specified
    if args.headless:
        settings.headless_mode = True
    
    # Create CLI instance
    cli = AEMAgentCLI()
    
    try:
        if args.command:
            # Single command mode
            success = asyncio.run(cli.run_single_command(args.command))
            sys.exit(0 if success else 1)
        else:
            # Interactive mode (default)
            asyncio.run(cli.run_interactive_mode())
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
