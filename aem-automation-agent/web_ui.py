"""
Web UI for AEM Automation Agent
Provides a user-friendly web interface for interacting with the AEM agent
"""

from flask import Flask, render_template, request, jsonify, session
import asyncio
import threading
import uuid
from datetime import datetime
import os
import json
from aem_agent import AEMAgent
from prompt_parser import PromptParser
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variables
active_sessions = {}
parser = PromptParser()

class WebAEMAgent:
    """Wrapper for AEMAgent to work with web interface"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.agent = None
        self.status = "idle"
        self.current_task = None
        self.logs = []
        self.screenshots = []
    
    async def initialize(self):
        """Initialize the AEM agent"""
        try:
            self.agent = AEMAgent()
            await self.agent.start()
            self.add_log("Agent browser started successfully", "success")
            
            # Attempt to login to AEM
            self.add_log("Attempting to login to AEM...", "info")
            login_success = await self.agent.login()
            
            if login_success:
                self.status = "ready"
                self.add_log("Successfully logged in to AEM", "success")
                self.add_log("Agent ready for commands", "success")
                return True
            else:
                self.status = "error"
                self.add_log("Failed to login to AEM. Please check your credentials in .env file", "error")
                self.add_log("Make sure AEM_USERNAME and AEM_PASSWORD are set correctly", "error")
                return False
                
        except Exception as e:
            self.add_log(f"Failed to initialize agent: {str(e)}", "error")
            self.status = "error"
            return False
    
    async def execute_command(self, command):
        """Execute a natural language command"""
        try:
            self.status = "working"
            self.current_task = command
            self.add_log(f"Executing: {command}", "info")
            
            # Parse the command
            parsed = parser.parse_prompt(command)
            self.add_log(f"Parsed {len(parsed.actions)} actions", "info")
            
            # Generate execution plan
            plan = parser.generate_execution_plan(parsed)
            for step in plan:
                self.add_log(f"Plan: {step}", "info")
            
            # Execute with the agent
            result = await self.agent.execute_prompt(command)
            
            if result.get('success'):
                self.add_log("Command executed successfully!", "success")
                if result.get('screenshot'):
                    self.screenshots.append({
                        'timestamp': datetime.now().isoformat(),
                        'command': command,
                        'path': result['screenshot']
                    })
            else:
                self.add_log(f"Command failed: {result.get('error', 'Unknown error')}", "error")
            
            self.status = "ready"
            self.current_task = None
            return result
            
        except Exception as e:
            self.add_log(f"Error executing command: {str(e)}", "error")
            self.status = "error"
            self.current_task = None
            return {'success': False, 'error': str(e)}
    
    def add_log(self, message, level="info"):
        """Add a log entry"""
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'level': level
        })
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
    
    async def cleanup(self):
        """Clean up the agent"""
        if self.agent:
            await self.agent.stop()
        self.status = "stopped"

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new agent session"""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    web_agent = WebAEMAgent(session_id)
    active_sessions[session_id] = web_agent
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'status': web_agent.status
    })

@app.route('/api/session/initialize', methods=['POST'])
def initialize_session():
    """Initialize the AEM agent for the session"""
    session_id = session.get('session_id')
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    web_agent = active_sessions[session_id]
    
    # Run initialization in background
    def init_agent():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(web_agent.initialize())
        loop.close()
    
    thread = threading.Thread(target=init_agent)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Initialization started'})

@app.route('/api/command/execute', methods=['POST'])
def execute_command():
    """Execute a natural language command"""
    session_id = session.get('session_id')
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    data = request.get_json()
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})
    
    web_agent = active_sessions[session_id]
    
    if web_agent.status != "ready":
        return jsonify({'success': False, 'error': f'Agent not ready (status: {web_agent.status})'})
    
    # Execute command in background
    def execute_cmd():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(web_agent.execute_command(command))
        loop.close()
    
    thread = threading.Thread(target=execute_cmd)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Command execution started'})

@app.route('/api/session/status')
def get_session_status():
    """Get current session status"""
    session_id = session.get('session_id')
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    web_agent = active_sessions[session_id]
    
    return jsonify({
        'success': True,
        'status': web_agent.status,
        'current_task': web_agent.current_task,
        'logs': web_agent.logs[-10:],  # Last 10 logs
        'screenshots': web_agent.screenshots[-5:]  # Last 5 screenshots
    })

@app.route('/api/session/logs')
def get_session_logs():
    """Get all session logs"""
    session_id = session.get('session_id')
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    web_agent = active_sessions[session_id]
    
    return jsonify({
        'success': True,
        'logs': web_agent.logs
    })

@app.route('/api/parser/test', methods=['POST'])
def test_parser():
    """Test the prompt parser without executing"""
    data = request.get_json()
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})
    
    try:
        parsed = parser.parse_prompt(command)
        plan = parser.generate_execution_plan(parsed)
        
        return jsonify({
            'success': True,
            'parsed': {
                'page_name': parsed.page_name,
                'page_title': parsed.page_title,
                'target_path': parsed.target_path,
                'actions': [
                    {
                        'type': action.action_type,
                        'parameters': action.parameters
                    }
                    for action in parsed.actions
                ]
            },
            'execution_plan': plan
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/session/cleanup', methods=['POST'])
def cleanup_session():
    """Clean up the current session"""
    session_id = session.get('session_id')
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    web_agent = active_sessions[session_id]
    
    # Cleanup in background
    def cleanup_agent():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(web_agent.cleanup())
        loop.close()
    
    thread = threading.Thread(target=cleanup_agent)
    thread.start()
    
    # Remove from active sessions
    del active_sessions[session_id]
    session.pop('session_id', None)
    
    return jsonify({'success': True, 'message': 'Session cleaned up'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting AEM Automation Agent Web UI...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🔧 Make sure to configure your .env file with AEM credentials")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
