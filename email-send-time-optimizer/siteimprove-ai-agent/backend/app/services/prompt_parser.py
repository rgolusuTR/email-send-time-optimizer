"""
Natural language prompt parser for Siteimprove commands
"""
import re
from typing import Dict, List, Optional, Any
from loguru import logger

class PromptParser:
    """Parses natural language commands into actionable intents"""
    
    def __init__(self):
        self.intent_patterns = {
            "login": [
                r"login\s+to\s+siteimprove",
                r"log\s+in",
                r"sign\s+in",
                r"authenticate"
            ],
            "scan": [
                r"scan\s+for\s+broken\s+links",
                r"get\s+broken\s+links",
                r"show\s+me\s+broken\s+links",
                r"fetch\s+broken\s+links",
                r"retrieve\s+broken\s+links",
                r"broken\s+links\s+report"
            ],
            "filter": [
                r"show\s+.*with\s+more\s+than\s+(\d+)\s+clicks",
                r"filter\s+by\s+clicks\s+greater\s+than\s+(\d+)",
                r"pages\s+with\s+(\d+)\s+or\s+more\s+clicks",
                r"show\s+.*with\s+(\d+)\+\s+page\s+views",
                r"filter\s+.*page\s+level\s+(\d+)"
            ],
            "export": [
                r"export\s+.*to\s+csv",
                r"download\s+.*csv",
                r"save\s+.*csv",
                r"export\s+data",
                r"generate\s+report"
            ],
            "analyze": [
                r"which\s+pages\s+have\s+the\s+most\s+.*broken\s+links",
                r"prioritize\s+.*fixes",
                r"most\s+critical\s+.*issues",
                r"analyze\s+.*data",
                r"show\s+.*priority"
            ],
            "compare": [
                r"compare\s+.*from\s+last\s+week",
                r"show\s+.*trends",
                r"compare\s+.*previous",
                r"changes\s+since"
            ],
            "help": [
                r"help",
                r"what\s+can\s+you\s+do",
                r"commands",
                r"how\s+to"
            ]
        }
        
        self.parameter_patterns = {
            "clicks": r"(\d+)\s+clicks?",
            "page_views": r"(\d+)\s+page\s+views?",
            "broken_links": r"(\d+)\s+broken\s+links?",
            "page_level": r"page\s+level\s+(\d+)",
            "time_period": r"(last\s+week|yesterday|today|last\s+month)",
            "format": r"(csv|json|excel|xlsx)"
        }
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into structured command
        """
        prompt_lower = prompt.lower().strip()
        
        # Identify intent
        intent = self._identify_intent(prompt_lower)
        
        # Extract parameters
        parameters = self._extract_parameters(prompt_lower)
        
        # Generate action plan
        actions = self._generate_actions(intent, parameters)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(intent, parameters)
        
        return {
            "intent": intent,
            "parameters": parameters,
            "actions": actions,
            "suggestions": suggestions,
            "original_prompt": prompt
        }
    
    def _identify_intent(self, prompt: str) -> str:
        """Identify the main intent of the prompt"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    return intent
        
        # Default intent if no match found
        return "scan"
    
    def _extract_parameters(self, prompt: str) -> Dict[str, Any]:
        """Extract parameters from the prompt"""
        parameters = {}
        
        for param_name, pattern in self.parameter_patterns.items():
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                if param_name in ["clicks", "page_views", "broken_links", "page_level"]:
                    parameters[param_name] = int(match.group(1))
                else:
                    parameters[param_name] = match.group(1)
        
        # Extract comparison operators
        if "more than" in prompt or "greater than" in prompt or ">" in prompt:
            parameters["operator"] = "greater_than"
        elif "less than" in prompt or "<" in prompt:
            parameters["operator"] = "less_than"
        elif "equal to" in prompt or "exactly" in prompt:
            parameters["operator"] = "equal_to"
        
        return parameters
    
    def _generate_actions(self, intent: str, parameters: Dict[str, Any]) -> List[str]:
        """Generate a list of actions based on intent and parameters"""
        actions = []
        
        if intent == "login":
            actions = [
                "Initialize browser",
                "Navigate to Siteimprove",
                "Enter credentials",
                "Complete authentication"
            ]
        
        elif intent == "scan":
            actions = [
                "Ensure logged in to Siteimprove",
                "Navigate to Quality Assurance section",
                "Open Pages with broken links report",
                "Extract table data",
                "Process and return results"
            ]
        
        elif intent == "filter":
            actions = [
                "Get current broken links data",
                "Apply filters based on parameters",
                "Return filtered results"
            ]
            
            # Add specific filter actions
            if "clicks" in parameters:
                op = parameters.get("operator", "greater_than")
                actions.append(f"Filter pages with clicks {op} {parameters['clicks']}")
            
            if "page_views" in parameters:
                op = parameters.get("operator", "greater_than")
                actions.append(f"Filter pages with page views {op} {parameters['page_views']}")
        
        elif intent == "export":
            format_type = parameters.get("format", "csv")
            actions = [
                "Get current data",
                f"Format data for {format_type} export",
                f"Generate {format_type} file",
                "Provide download link"
            ]
        
        elif intent == "analyze":
            actions = [
                "Get broken links data",
                "Calculate priority scores",
                "Sort by importance",
                "Generate analysis report"
            ]
        
        elif intent == "compare":
            actions = [
                "Get current data",
                "Retrieve historical data",
                "Compare metrics",
                "Generate comparison report"
            ]
        
        elif intent == "help":
            actions = [
                "Display available commands",
                "Show usage examples",
                "Provide command syntax help"
            ]
        
        return actions
    
    def _generate_suggestions(self, intent: str, parameters: Dict[str, Any]) -> List[str]:
        """Generate helpful suggestions based on the command"""
        suggestions = []
        
        if intent == "scan":
            suggestions = [
                "Try: 'Show me broken links with more than 10 clicks'",
                "Try: 'Export the current results to CSV'",
                "Try: 'Which pages have the most critical issues?'"
            ]
        
        elif intent == "filter":
            suggestions = [
                "Try: 'Show pages with more than 5 page views'",
                "Try: 'Filter by page level 2'",
                "Try: 'Export filtered results to CSV'"
            ]
        
        elif intent == "export":
            suggestions = [
                "Try: 'Export to Excel format'",
                "Try: 'Include priority scores in export'",
                "Try: 'Export only high-priority issues'"
            ]
        
        elif intent == "analyze":
            suggestions = [
                "Try: 'Compare with last week's data'",
                "Try: 'Show trending issues'",
                "Try: 'Export priority analysis'"
            ]
        
        return suggestions
    
    def get_help_text(self) -> str:
        """Return help text with available commands"""
        help_text = """
Available Commands:

🔐 Login Commands:
• "Login to Siteimprove"
• "Sign in"

📊 Data Commands:
• "Show me broken links"
• "Scan for broken links"
• "Get broken links report"

🔍 Filter Commands:
• "Show broken links with more than 10 clicks"
• "Filter by page level 2"
• "Pages with 5+ page views"

📈 Analysis Commands:
• "Which pages have the most broken links?"
• "Prioritize fixes based on page views"
• "Show most critical issues"

📁 Export Commands:
• "Export to CSV"
• "Download current data"
• "Generate report"

📊 Comparison Commands:
• "Compare with last week"
• "Show trends"
• "Changes since yesterday"

Examples:
• "Login to Siteimprove and show me broken links with more than 5 clicks"
• "Export pages with high priority issues to CSV"
• "Which pages have the most critical broken links?"
        """
        return help_text.strip()
