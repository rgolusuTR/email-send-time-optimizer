"""
Siteimprove automation service using Playwright
Based on the user's recorded workflow
"""
import asyncio
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
from loguru import logger
from datetime import datetime
import pandas as pd

from ..config import settings
from ..models.broken_link import BrokenLink

class SiteimproveAutomation:
    """Handles automation of Siteimprove website interactions"""
    
    def __init__(self, websocket_manager=None):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logged_in: bool = False
        self.playwright = None
        self.websocket_manager = websocket_manager
        
    async def start(self):
        """Initialize the browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=settings.headless_mode,
                timeout=settings.browser_timeout
            )
            
            # Create a new page with proper viewport
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({"width": 981, "height": 695})
            
            logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def stop(self):
        """Close the browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
                
            self.logged_in = False
            logger.info("Browser closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def login(self) -> bool:
        """
        Login to Siteimprove following the exact recorded workflow with progress updates
        """
        try:
            if self.websocket_manager:
                await self.websocket_manager.send_login_step("start", "🚀 Initializing browser and starting login process...")
            
            if not self.page:
                await self.start()
            
            logger.info("Starting Siteimprove login process...")
            
            # Step 1: Navigate to Siteimprove homepage
            if self.websocket_manager:
                await self.websocket_manager.send_login_step("navigate", "🌐 Navigating to Siteimprove homepage...")
            
            await self.page.goto(settings.siteimprove_base_url)
            logger.info("Navigated to Siteimprove homepage")
            
            # Wait for the page to load and look for login elements
            await self.page.wait_for_load_state("networkidle")
            
            if self.websocket_manager:
                await self.websocket_manager.send_login_step("page_loaded", "✅ Homepage loaded successfully")
            
            # Look for login button or direct navigation to login
            # This might redirect to the OAuth consent page automatically
            await self.page.wait_for_timeout(2000)
            
            # Step 2: Handle the OAuth flow - enter email
            try:
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("email_step", "📧 Entering email credentials...")
                
                # Wait for email field to appear
                await self.page.wait_for_selector("#Email", timeout=10000)
                await self.page.fill("#Email", settings.siteimprove_username)
                logger.info("Entered username")
                
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("email_entered", "✅ Email entered successfully")
                
                # Click Continue button
                await self.page.click("form > button:has-text('Continue')")
                await self.page.wait_for_load_state("networkidle")
                logger.info("Clicked Continue button")
                
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("continue_clicked", "✅ Continue button clicked, proceeding to password...")
                
            except Exception as e:
                logger.warning(f"Email step might have been skipped: {e}")
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("email_skipped", "⚠️ Email step skipped (already logged in or different flow)")
            
            # Step 3: Enter password
            try:
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("password_step", "🔐 Entering password...")
                
                await self.page.wait_for_selector("#Password", timeout=10000)
                await self.page.fill("#Password", settings.siteimprove_password)
                logger.info("Entered password")
                
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("password_entered", "✅ Password entered successfully")
                
                # Optional: Check "Keep me signed in"
                try:
                    keep_signed_in = self.page.locator("div.secondary-field label")
                    if await keep_signed_in.is_visible():
                        await keep_signed_in.click()
                        logger.info("Checked 'Keep me signed in'")
                        if self.websocket_manager:
                            await self.websocket_manager.send_login_step("keep_signed_in", "✅ 'Keep me signed in' option selected")
                except:
                    pass
                
                # Click login button
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("login_submit", "🔄 Submitting login credentials...")
                
                await self.page.click("form > button")
                await self.page.wait_for_load_state("networkidle")
                logger.info("Clicked login button")
                
            except Exception as e:
                logger.error(f"Password step failed: {e}")
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("password_failed", f"❌ Password step failed: {str(e)}", False)
                return False
            
            # Step 4: Wait for successful login and dashboard
            try:
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("verifying", "🔍 Verifying login success and loading dashboard...")
                
                # Wait for dashboard elements to appear
                await self.page.wait_for_selector("div.site > a > span", timeout=15000)
                logger.info("Successfully logged in to Siteimprove")
                self.logged_in = True
                
                # Take a screenshot for verification
                await self.page.screenshot(path=f"{settings.screenshot_path}/login_success.png")
                
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("success", "🎉 Login successful! Dashboard loaded and ready to use.")
                
                return True
                
            except Exception as e:
                logger.error(f"Login verification failed: {e}")
                if self.websocket_manager:
                    await self.websocket_manager.send_login_step("verification_failed", f"❌ Login verification failed: {str(e)}", False)
                return False
                
        except Exception as e:
            logger.error(f"Login process failed: {e}")
            if self.websocket_manager:
                await self.websocket_manager.send_login_step("failed", f"❌ Login process failed: {str(e)}", False)
            return False
    
    async def navigate_to_broken_links(self) -> bool:
        """
        Navigate to the 'Pages with broken links' report with progress updates
        Following the exact recorded workflow
        """
        try:
            if not self.logged_in:
                logger.error("Not logged in. Please login first.")
                if self.websocket_manager:
                    await self.websocket_manager.send_scan_step("not_logged_in", "❌ Not logged in. Please login first.", success=False)
                return False
            
            logger.info("Navigating to broken links report...")
            if self.websocket_manager:
                await self.websocket_manager.send_scan_step("start_navigation", "🧭 Starting navigation to broken links report...")
            
            # Step 1: Click on the site/dashboard area
            if self.websocket_manager:
                await self.websocket_manager.send_scan_step("dashboard", "📊 Accessing site dashboard...", 20)
            
            await self.page.click("div.site > a > span")
            await self.page.wait_for_load_state("networkidle")
            logger.info("Clicked on site dashboard")
            
            # Step 2: Navigate to Quality Assurance section
            if self.websocket_manager:
                await self.websocket_manager.send_scan_step("quality_assurance", "🔍 Opening Quality Assurance section...", 40)
            
            await self.page.click("li:nth-of-type(5) div.side-navigation_main-nav-title__FiTL8")
            await self.page.wait_for_timeout(1000)
            logger.info("Clicked Quality Assurance section")
            
            # Step 3: Click on Links subsection
            if self.websocket_manager:
                await self.websocket_manager.send_scan_step("links_section", "🔗 Navigating to Links subsection...", 60)
            
            await self.page.click("div.side-navigation_sub-nav__1N91m > div > div.side-navigation_shown__2jqE2 li:nth-of-type(3) > button")
            await self.page.wait_for_timeout(1000)
            logger.info("Clicked Links subsection")
            
            # Step 4: Click on "Pages with broken links"
            if self.websocket_manager:
                await self.websocket_manager.send_scan_step("broken_links_report", "📋 Loading broken links report...", 80)
            
            await self.page.click("text/Pages with broken")
            await self.page.wait_for_load_state("networkidle")
            logger.info("Navigated to Pages with broken links report")
            
            # Take a screenshot for verification
            await self.page.screenshot(path=f"{settings.screenshot_path}/broken_links_page.png")
            
            if self.websocket_manager:
                await self.websocket_manager.send_scan_step("navigation_complete", "✅ Successfully navigated to broken links report", 100)
            
            return True
            
        except Exception as e:
            logger.error(f"Navigation to broken links failed: {e}")
            if self.websocket_manager:
                await self.websocket_manager.send_scan_step("navigation_failed", f"❌ Navigation failed: {str(e)}", success=False)
            return False
    
    async def extract_broken_links_data(self) -> List[BrokenLink]:
        """
        Extract broken links data from the table
        """
        try:
            logger.info("Extracting broken links data...")
            
            # Wait for the table to load
            await self.page.wait_for_selector("table", timeout=10000)
            
            # Extract table data
            rows = await self.page.query_selector_all("table tbody tr")
            broken_links_data = []
            
            for row in rows:
                try:
                    # Extract data from each column
                    title_element = await row.query_selector("th div button div span.title-url_title_2no6K")
                    url_element = await row.query_selector("th div button div span.title-url_url_1Xo8p")
                    broken_links_element = await row.query_selector("td:nth-child(2)")
                    clicks_element = await row.query_selector("td:nth-child(3)")
                    page_level_element = await row.query_selector("td:nth-child(4)")
                    page_views_element = await row.query_selector("td:nth-child(5)")
                    
                    if title_element and url_element:
                        title = await title_element.text_content()
                        url = await url_element.text_content()
                        broken_links = int(await broken_links_element.text_content() or "0")
                        clicks = int(await clicks_element.text_content() or "0")
                        page_level = int(await page_level_element.text_content() or "0")
                        page_views = int(await page_views_element.text_content() or "0")
                        
                        broken_link = BrokenLink(
                            title=title.strip(),
                            url=url.strip(),
                            broken_links=broken_links,
                            clicks=clicks,
                            page_level=page_level,
                            page_views=page_views,
                            last_updated=datetime.now()
                        )
                        
                        broken_links_data.append(broken_link)
                        
                except Exception as e:
                    logger.warning(f"Failed to extract data from row: {e}")
                    continue
            
            logger.info(f"Extracted {len(broken_links_data)} broken link entries")
            return broken_links_data
            
        except Exception as e:
            logger.error(f"Failed to extract broken links data: {e}")
            return []
    
    async def get_broken_links_report(self, force_refresh: bool = False) -> List[BrokenLink]:
        """
        Complete workflow to get broken links report
        """
        try:
            # Start browser if not already started
            if not self.browser:
                await self.start()
            
            # Login if not already logged in
            if not self.logged_in:
                login_success = await self.login()
                if not login_success:
                    raise Exception("Failed to login to Siteimprove")
            
            # Navigate to broken links report
            nav_success = await self.navigate_to_broken_links()
            if not nav_success:
                raise Exception("Failed to navigate to broken links report")
            
            # Extract data
            broken_links_data = await self.extract_broken_links_data()
            
            return broken_links_data
            
        except Exception as e:
            logger.error(f"Failed to get broken links report: {e}")
            raise
    
    async def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current page"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = f"{settings.screenshot_path}/{filename}"
            await self.page.screenshot(path=filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
