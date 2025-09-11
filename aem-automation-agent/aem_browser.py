import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from loguru import logger
from config import settings
from typing import Optional, Dict, Any

class AEMBrowser:
    """Browser automation class for AEM interactions"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def start(self):
        """Initialize browser and create context"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=settings.headless_mode,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1435, 'height': 800}
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(settings.browser_timeout)
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def close(self):
        """Close browser and cleanup resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def login_to_aem(self, username: str, password: str) -> bool:
        """Login to AEM using provided credentials"""
        try:
            logger.info("Starting AEM login process")
            
            # Navigate to AEM start page
            await self.page.goto(f"{settings.aem_base_url}/aem/start")
            
            # Wait for password field and enter credentials
            await self.page.wait_for_selector("#password", timeout=10000)
            await self.page.fill("#password", password)
            
            # Click sign on button
            await self.page.click("#signOnButton")
            
            # Wait for navigation to complete
            await self.page.wait_for_load_state("networkidle")
            
            # Check if login was successful by looking for AEM interface elements
            try:
                await self.page.wait_for_selector("coral-masonry", timeout=10000)
                logger.info("Login successful")
                return True
            except:
                logger.error("Login failed - AEM interface not found")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def navigate_to_sites(self):
        """Navigate to Sites section"""
        try:
            logger.info("Navigating to Sites")
            # Click on Sites icon
            await self.page.click("coral-masonry-item:nth-of-type(4) coral-icon")
            await self.page.wait_for_load_state("networkidle")
            logger.info("Successfully navigated to Sites")
        except Exception as e:
            logger.error(f"Failed to navigate to Sites: {e}")
            raise
    
    async def navigate_to_path(self, path_segments: list):
        """Navigate through folder structure using path segments"""
        try:
            logger.info(f"Navigating to path: {' -> '.join(path_segments)}")
            
            for segment in path_segments:
                # Look for the folder with the given name
                folder_selector = f"text/{segment}"
                await self.page.wait_for_selector(folder_selector, timeout=5000)
                await self.page.click(folder_selector)
                await self.page.wait_for_load_state("networkidle")
                logger.info(f"Navigated to: {segment}")
                
        except Exception as e:
            logger.error(f"Failed to navigate to path: {e}")
            raise
    
    async def create_page(self, page_name: str, page_title: str, template_index: int = 49) -> bool:
        """Create a new page with specified name and title"""
        try:
            logger.info(f"Creating page: {page_name}")
            
            # Click Create button
            await self.page.click("button.granite-collection-create")
            await asyncio.sleep(1)
            
            # Click Page option
            await self.page.click("coral-shell a.cq-siteadmin-admin-createpage")
            await self.page.wait_for_load_state("networkidle")
            
            # Select template (using the index from the recording)
            template_selector = f"coral-masonry-item:nth-of-type({template_index}) img"
            await self.page.wait_for_selector(template_selector, timeout=10000)
            await self.page.click(template_selector)
            
            # Click Next
            await self.page.click("coral-panel.is-selected button")
            await asyncio.sleep(1)
            
            # Fill in page details
            await self.page.fill("#coral-id-72", page_name)  # Page name
            await self.page.fill("#coral-id-73", page_title)  # Page title
            
            # Fill other required fields based on the recording
            await self.page.fill("#coral-id-74", page_title)  # Description
            await self.page.fill("#coral-id-75", "o")  # Some field
            
            # Select from dropdown options (based on recording pattern)
            await self.page.click("button:nth-of-type(1) coral-list-item-content")
            
            # Fill more fields
            await self.page.fill("#coral-id-76", "g")
            await self.page.click("div:nth-of-type(6) button:nth-of-type(2) coral-list-item-content")
            
            await self.page.fill("#coral-id-77", "g")
            await self.page.click("div:nth-of-type(7) button:nth-of-type(9) coral-list-item-content")
            
            # Click Create
            await self.page.click("coral-panel.is-selected button.coral3-Button--primary")
            await asyncio.sleep(2)
            
            # Confirm creation
            await self.page.click("coral-dialog button.coral3-Button--primary")
            await self.page.wait_for_load_state("networkidle")
            
            logger.info(f"Page '{page_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create page: {e}")
            return False
    
    async def open_page_editor(self, page_name: str):
        """Open the page editor for the specified page"""
        try:
            logger.info(f"Opening editor for page: {page_name}")
            
            # Find and click the page to edit
            page_selector = f"text/{page_name}"
            await self.page.wait_for_selector(page_selector, timeout=10000)
            await self.page.click(page_selector)
            
            # The page should automatically open in editor mode
            await self.page.wait_for_load_state("networkidle")
            logger.info("Page editor opened successfully")
            
        except Exception as e:
            logger.error(f"Failed to open page editor: {e}")
            raise
    
    async def add_component(self, component_name: str = "Article Paragraph"):
        """Add a component to the page"""
        try:
            logger.info(f"Adding component: {component_name}")
            
            # Click on the container to add component
            await self.page.click("div.cq-draggable > div > div")
            await asyncio.sleep(1)
            
            # Click the add component button
            await self.page.click("#OverlayWrapper button:nth-of-type(1) > coral-icon")
            await asyncio.sleep(1)
            
            # Select the component from the list
            component_selector = f"text/{component_name}"
            await self.page.click(component_selector)
            await asyncio.sleep(2)
            
            logger.info(f"Component '{component_name}' added successfully")
            
        except Exception as e:
            logger.error(f"Failed to add component: {e}")
            raise
    
    async def edit_component_content(self, content: str):
        """Edit the content of a component"""
        try:
            logger.info("Editing component content")
            
            # Click on the component to select it
            await self.page.click("div.cq-draggable > div > div.cq-draggable")
            await asyncio.sleep(1)
            
            # Click edit button
            await self.page.click("#OverlayWrapper button:nth-of-type(1) > coral-icon")
            await asyncio.sleep(2)
            
            # Find the rich text editor and add content
            editor_selector = "div.rte-editorWrapper > div"
            await self.page.wait_for_selector(editor_selector, timeout=10000)
            await self.page.click(editor_selector)
            await self.page.fill(editor_selector, content)
            
            # Exit edit mode
            await self.page.click("#FullScreenWrapper div:nth-of-type(4) button.rte--modechanger > coral-icon")
            await asyncio.sleep(1)
            
            logger.info("Component content updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to edit component content: {e}")
            raise
    
    async def preview_page(self):
        """Preview the page as published"""
        try:
            logger.info("Opening page preview")
            
            # Click page info button
            await self.page.click("coral-actionbar-primary > coral-actionbar-item:nth-of-type(2) coral-icon")
            await asyncio.sleep(1)
            
            # Click View as Published
            await self.page.click("button.pageinfo-viewaspublished")
            await self.page.wait_for_load_state("networkidle")
            
            logger.info("Page preview opened successfully")
            
        except Exception as e:
            logger.error(f"Failed to open page preview: {e}")
            raise
    
    async def take_screenshot(self, filename: str = "screenshot.png"):
        """Take a screenshot of the current page"""
        try:
            await self.page.screenshot(path=filename)
            logger.info(f"Screenshot saved as {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
