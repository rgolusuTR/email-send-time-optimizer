import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from loguru import logger

class AEMAction(BaseModel):
    """Represents a single AEM action to be performed"""
    action_type: str
    parameters: Dict[str, Any]

class ParsedPrompt(BaseModel):
    """Represents a parsed user prompt with extracted actions"""
    original_prompt: str
    actions: List[AEMAction]
    target_path: Optional[List[str]] = None
    page_name: Optional[str] = None
    page_title: Optional[str] = None

class PromptParser:
    """Parses natural language prompts into structured AEM actions"""
    
    def __init__(self):
        self.action_patterns = {
            'create_page': [
                r'create.*page.*(?:called|named)\s+["\']?([^"\']+)["\']?',
                r'make.*new.*page.*["\']?([^"\']+)["\']?',
                r'add.*page.*["\']?([^"\']+)["\']?'
            ],
            'add_component': [
                r'add.*(?:an?|the)?\s*([^,]+?)\s*(?:component|element)',
                r'insert.*(?:an?|the)?\s*([^,]+?)\s*(?:component|element)',
                r'place.*(?:an?|the)?\s*([^,]+?)\s*(?:component|element)',
                r'add.*(?:component|element).*["\']?([^"\']+)["\']?',
                r'insert.*(?:component|element).*["\']?([^"\']+)["\']?',
                r'place.*(?:component|element).*["\']?([^"\']+)["\']?'
            ],
            'edit_content': [
                r'(?:fill|update|edit|change).*(?:with|to)\s+["\']?([^"\']+)["\']?',
                r'(?:content|text).*["\']?([^"\']+)["\']?',
                r'write.*["\']?([^"\']+)["\']?'
            ],
            'navigate_to': [
                r'(?:go to|navigate to|open)\s+([^,]+)',
                r'(?:in|under)\s+([^,]+)(?:\s+folder|\s+directory)?'
            ]
        }
        
        self.component_mappings = {
            'paragraph': 'Article Paragraph',
            'article paragraph': 'Article Paragraph',
            'text': 'Article Paragraph',
            'content': 'Article Paragraph',
            'hero': 'Hero Banner',
            'banner': 'Hero Banner',
            'image': 'Image',
            'title': 'Title',
            'heading': 'Title'
        }
    
    def parse_prompt(self, prompt: str) -> ParsedPrompt:
        """Parse a natural language prompt into structured actions"""
        logger.info(f"Parsing prompt: {prompt}")
        
        actions = []
        page_name = None
        page_title = None
        target_path = None
        
        # Extract page creation
        page_match = self._extract_page_info(prompt)
        if page_match:
            page_name = page_match.get('name')
            page_title = page_match.get('title', page_name)
            actions.append(AEMAction(
                action_type='create_page',
                parameters={
                    'page_name': page_name,
                    'page_title': page_title
                }
            ))
        
        # Extract navigation path
        path_match = self._extract_navigation_path(prompt)
        if path_match:
            target_path = path_match
        
        # Extract component additions
        component_matches = self._extract_components(prompt)
        for component in component_matches:
            actions.append(AEMAction(
                action_type='add_component',
                parameters={
                    'component_name': component
                }
            ))
        
        # Extract content updates
        content_matches = self._extract_content(prompt)
        for content in content_matches:
            actions.append(AEMAction(
                action_type='edit_content',
                parameters={
                    'content': content
                }
            ))
        
        parsed = ParsedPrompt(
            original_prompt=prompt,
            actions=actions,
            target_path=target_path,
            page_name=page_name,
            page_title=page_title
        )
        
        logger.info(f"Parsed {len(actions)} actions from prompt")
        return parsed
    
    def _extract_page_info(self, prompt: str) -> Optional[Dict[str, str]]:
        """Extract page name and title from prompt"""
        patterns = [
            r'create.*page.*(?:called|named)\s+["\']?([^"\']+)["\']?',
            r'make.*new.*page.*["\']?([^"\']+)["\']?',
            r'add.*page.*["\']?([^"\']+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Convert to URL-friendly format
                url_name = re.sub(r'[^a-zA-Z0-9\-]', '-', name.lower())
                return {
                    'name': url_name,
                    'title': name
                }
        return None
    
    def _extract_navigation_path(self, prompt: str) -> Optional[List[str]]:
        """Extract navigation path from prompt"""
        patterns = [
            r'(?:in|under)\s+([^,]+?)(?:\s+folder|\s+directory|,|$)',
            r'(?:go to|navigate to)\s+([^,]+?)(?:,|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                path_str = match.group(1).strip()
                # Split by common separators and clean up
                path_segments = [seg.strip() for seg in re.split(r'[>/\\]', path_str) if seg.strip()]
                return path_segments
        
        # Default path based on the recording
        return ['ewp-marketing-websites', 'test-site', 'gl', 'en', 'tax', 'Joseph test']
    
    def _extract_components(self, prompt: str) -> List[str]:
        """Extract component names from prompt"""
        components = []
        
        patterns = [
            r'add.*(?:an?|the)?\s*([^,]+?)\s*(?:component|element)',
            r'insert.*(?:an?|the)?\s*([^,]+?)\s*(?:component|element)',
            r'place.*(?:an?|the)?\s*([^,]+?)\s*(?:component|element)',
            r'add.*(?:component|element).*["\']?([^"\']+)["\']?',
            r'insert.*(?:component|element).*["\']?([^"\']+)["\']?',
            r'place.*(?:component|element).*["\']?([^"\']+)["\']?'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            for match in matches:
                component_name = match.group(1).strip().lower()
                # Map to actual AEM component name
                mapped_component = self.component_mappings.get(component_name, 'Article Paragraph')
                components.append(mapped_component)
        
        # If no specific component mentioned but content is mentioned, assume Article Paragraph
        if not components and any(word in prompt.lower() for word in ['content', 'text', 'write', 'fill']):
            components.append('Article Paragraph')
        
        return components
    
    def _extract_content(self, prompt: str) -> List[str]:
        """Extract content to be added from prompt"""
        content_list = []
        
        patterns = [
            r'(?:fill|update|edit|change).*(?:with|to)\s+["\']([^"\']+)["\']',
            r'(?:content|text).*["\']([^"\']+)["\']',
            r'write\s+["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            for match in matches:
                content = match.group(1).strip()
                content_list.append(content)
        
        return content_list
    
    def generate_execution_plan(self, parsed_prompt: ParsedPrompt) -> List[str]:
        """Generate a human-readable execution plan"""
        plan = []
        
        if parsed_prompt.target_path:
            plan.append(f"1. Navigate to: {' -> '.join(parsed_prompt.target_path)}")
        
        step = 2 if parsed_prompt.target_path else 1
        
        for action in parsed_prompt.actions:
            if action.action_type == 'create_page':
                plan.append(f"{step}. Create page '{action.parameters['page_name']}' with title '{action.parameters['page_title']}'")
                step += 1
            elif action.action_type == 'add_component':
                plan.append(f"{step}. Add {action.parameters['component_name']} component")
                step += 1
            elif action.action_type == 'edit_content':
                plan.append(f"{step}. Update content with: '{action.parameters['content']}'")
                step += 1
        
        return plan
