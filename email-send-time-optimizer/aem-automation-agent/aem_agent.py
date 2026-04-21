import asyncio
from typing import Optional
from loguru import logger
from aem_browser import AEMBrowser
from prompt_parser import PromptParser, ParsedPrompt
from config import settings

class AEMAgent:
    """Main AI agent for AEM automation"""
    
    def __init__(self):
        self.browser = AEMBrowser()
        self.parser = PromptParser()
        self.is_logged_in = False
        
    async def start(self):
        """Initialize the agent and browser"""
        try:
            await self.browser.start()
            logger.info("AEM Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AEM Agent: {e}")
            raise
    
    async def stop(self):
        """Cleanup and close the agent"""
        try:
            await self.browser.close()
            logger.info("AEM Agent stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping AEM Agent: {e}")
    
    async def login(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Login to AEM"""
        try:
            username = username or settings.aem_username
            password = password or settings.aem_password
            
            if not username or not password:
                logger.error("Username and password are required for login")
                return False
            
            success = await self.browser.login_to_aem(username, password)
            self.is_logged_in = success
            return success
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def execute_prompt(self, prompt: str) -> dict:
        """Execute a natural language prompt"""
        try:
            logger.info(f"Executing prompt: {prompt}")
            
            if not self.is_logged_in:
                logger.error("Not logged in to AEM. Please login first.")
                return {
                    "success": False,
                    "error": "Not logged in to AEM",
                    "actions_completed": []
                }
            
            # Parse the prompt
            parsed_prompt = self.parser.parse_prompt(prompt)
            
            # Generate execution plan
            execution_plan = self.parser.generate_execution_plan(parsed_prompt)
            logger.info("Execution plan:")
            for step in execution_plan:
                logger.info(f"  {step}")
            
            # Execute the actions
            result = await self._execute_actions(parsed_prompt)
            
            return {
                "success": result["success"],
                "prompt": prompt,
                "execution_plan": execution_plan,
                "actions_completed": result["actions_completed"],
                "error": result.get("error")
            }
            
        except Exception as e:
            logger.error(f"Failed to execute prompt: {e}")
            return {
                "success": False,
                "error": str(e),
                "actions_completed": []
            }
    
    async def _execute_actions(self, parsed_prompt: ParsedPrompt) -> dict:
        """Execute the parsed actions"""
        actions_completed = []
        
        try:
            # Navigate to Sites first
            await self.browser.navigate_to_sites()
            actions_completed.append("Navigated to Sites")
            
            # Navigate to target path if specified
            if parsed_prompt.target_path:
                await self.browser.navigate_to_path(parsed_prompt.target_path)
                actions_completed.append(f"Navigated to: {' -> '.join(parsed_prompt.target_path)}")
            
            # Execute each action in sequence
            for action in parsed_prompt.actions:
                if action.action_type == 'create_page':
                    success = await self._execute_create_page(action.parameters)
                    if success:
                        actions_completed.append(f"Created page: {action.parameters['page_name']}")
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to create page: {action.parameters['page_name']}",
                            "actions_completed": actions_completed
                        }
                
                elif action.action_type == 'add_component':
                    success = await self._execute_add_component(action.parameters)
                    if success:
                        actions_completed.append(f"Added component: {action.parameters['component_name']}")
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to add component: {action.parameters['component_name']}",
                            "actions_completed": actions_completed
                        }
                
                elif action.action_type == 'edit_content':
                    success = await self._execute_edit_content(action.parameters)
                    if success:
                        actions_completed.append(f"Updated content: {action.parameters['content'][:50]}...")
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to update content",
                            "actions_completed": actions_completed
                        }
            
            # Take a screenshot of the final result
            await self.browser.take_screenshot("final_result.png")
            actions_completed.append("Screenshot saved as final_result.png")
            
            return {
                "success": True,
                "actions_completed": actions_completed
            }
            
        except Exception as e:
            logger.error(f"Error executing actions: {e}")
            return {
                "success": False,
                "error": str(e),
                "actions_completed": actions_completed
            }
    
    async def _execute_create_page(self, parameters: dict) -> bool:
        """Execute page creation action"""
        try:
            success = await self.browser.create_page(
                page_name=parameters['page_name'],
                page_title=parameters['page_title']
            )
            
            if success:
                # Open the page editor after creation
                await self.browser.open_page_editor(parameters['page_name'])
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create page: {e}")
            return False
    
    async def _execute_add_component(self, parameters: dict) -> bool:
        """Execute add component action"""
        try:
            await self.browser.add_component(parameters['component_name'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to add component: {e}")
            return False
    
    async def _execute_edit_content(self, parameters: dict) -> bool:
        """Execute edit content action"""
        try:
            await self.browser.edit_component_content(parameters['content'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to edit content: {e}")
            return False
    
    async def preview_page(self):
        """Preview the current page"""
        try:
            await self.browser.preview_page()
            logger.info("Page preview opened")
        except Exception as e:
            logger.error(f"Failed to open page preview: {e}")
    
    async def take_screenshot(self, filename: str = "screenshot.png"):
        """Take a screenshot of the current page"""
        try:
            await self.browser.take_screenshot(filename)
            logger.info(f"Screenshot saved as {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")

# Example usage functions
async def demo_workflow():
    """Demonstrate the agent with a sample workflow"""
    agent = AEMAgent()
    
    try:
        # Initialize the agent
        await agent.start()
        
        # Login (you'll need to set credentials in .env file)
        login_success = await agent.login()
        if not login_success:
            logger.error("Login failed. Please check your credentials in .env file")
            return
        
        # Execute a sample prompt
        prompt = "Create a new page called 'AI Test Page', add an Article Paragraph component, and fill it with 'This content was created by AI automation!'"
        
        result = await agent.execute_prompt(prompt)
        
        if result["success"]:
            logger.info("Workflow completed successfully!")
            logger.info("Actions completed:")
            for action in result["actions_completed"]:
                logger.info(f"  ✓ {action}")
        else:
            logger.error(f"Workflow failed: {result['error']}")
            logger.info("Actions completed before failure:")
            for action in result["actions_completed"]:
                logger.info(f"  ✓ {action}")
    
    finally:
        await agent.stop()

if __name__ == "__main__":
    # Run the demo workflow
    asyncio.run(demo_workflow())
