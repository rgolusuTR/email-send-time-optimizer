# AEM Automation Agent

An AI-powered automation agent for Adobe Experience Manager (AEM) that can understand natural language instructions and perform page authoring tasks automatically.

## Features

- 🤖 **Natural Language Processing**: Give instructions in plain English
- 🔐 **Secure Authentication**: Login to AEM with your credentials
- 📄 **Page Creation**: Automatically create new pages with templates
- 🧩 **Component Management**: Add and configure AEM components
- ✏️ **Content Editing**: Update component content dynamically
- 🖼️ **Screenshot Capture**: Take screenshots of your work
- 📱 **Interactive CLI**: User-friendly command-line interface

## Installation

1. **Clone or download the project**

   ```bash
   cd aem-automation-agent
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**

   ```bash
   playwright install chromium
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your AEM credentials
   ```

## Configuration

Edit the `.env` file with your settings:

```env
# AEM Configuration
AEM_BASE_URL=https://author-prod-ams.ewp.thomsonreuters.com
AEM_USERNAME=your_username
AEM_PASSWORD=your_password

# Browser Configuration
HEADLESS_MODE=false
BROWSER_TIMEOUT=30000
```

## Usage

### Web User Interface (Recommended)

The easiest way to use the AEM Automation Agent is through the web interface:

```bash
# Start the web UI
python start_web_ui.py

# Or directly
python web_ui.py
```

Then open your browser to: **http://localhost:5000**

#### Web UI Features:

- 🎯 **Intuitive Interface**: Beautiful, user-friendly web dashboard
- 🤖 **Real-time Status**: Live updates on agent status and current tasks
- 📝 **Command Input**: Natural language command interface with examples
- 🔍 **Parser Preview**: Test and preview commands before execution
- 📊 **Activity Logs**: Real-time logging with different severity levels
- 📸 **Screenshots**: Automatic capture of AEM operations
- 💡 **Example Commands**: Click-to-use example workflows

### Interactive Mode (CLI)

Run the agent in interactive mode for the best command-line experience:

```bash
python cli.py
```

This will start an interactive session where you can:

- Give natural language instructions
- See real-time feedback
- Take screenshots
- Preview pages

### Single Command Mode

Execute a single instruction and exit:

```bash
python cli.py -c "Create a new page called 'Test Page'"
```

### Command Line Options

```bash
python cli.py --help
```

Options:

- `-c, --command`: Execute a single command
- `-i, --interactive`: Run in interactive mode
- `--headless`: Run browser in headless mode
- `--verbose`: Enable verbose logging

## Example Instructions

The agent understands natural language instructions like:

### Page Creation

- "Create a new page called 'Product Launch'"
- "Make a page named 'News Article' under the news folder"
- "Add a page called 'Contact Us'"

### Component Management

- "Add an Article Paragraph component"
- "Insert a Hero Banner component"
- "Place a Title component on the page"

### Content Editing

- "Fill the component with 'Welcome to our website'"
- "Update the content with 'Breaking news story'"
- "Write 'Contact us for more information'"

### Combined Instructions

- "Create a page called 'About Us', add a title component, and fill it with 'About Our Company'"
- "Make a news page, add an article paragraph, and write about the latest product launch"

## Architecture

The agent consists of several key components:

### Core Components

1. **AEMBrowser** (`aem_browser.py`)

   - Handles browser automation using Playwright
   - Manages AEM login and navigation
   - Performs page creation and component manipulation

2. **PromptParser** (`prompt_parser.py`)

   - Parses natural language instructions
   - Extracts actions and parameters
   - Maps user intent to AEM operations

3. **AEMAgent** (`aem_agent.py`)

   - Main orchestrator class
   - Coordinates between parser and browser
   - Manages execution flow and error handling

4. **CLI** (`cli.py`)
   - Command-line interface
   - Interactive and single-command modes
   - User-friendly feedback and help

### Workflow

1. **Parse**: Natural language instruction is parsed into structured actions
2. **Plan**: Execution plan is generated and logged
3. **Execute**: Actions are performed in sequence:
   - Login to AEM
   - Navigate to target location
   - Create pages
   - Add components
   - Update content
4. **Feedback**: Results and screenshots are provided

## Supported AEM Operations

### Authentication

- ✅ Login with username/password
- ✅ Session management
- ✅ Error handling for failed authentication

### Navigation

- ✅ Navigate to Sites section
- ✅ Browse folder structure
- ✅ Path-based navigation

### Page Management

- ✅ Create new pages with templates
- ✅ Set page properties (name, title, description)
- ✅ Open page editor

### Component Operations

- ✅ Add Article Paragraph components
- ✅ Edit component content
- ✅ Rich text editing
- 🔄 Additional component types (planned)

### Utilities

- ✅ Take screenshots
- ✅ Preview pages
- ✅ Error recovery

## Troubleshooting

### Common Issues

1. **Login Failed**

   - Check your credentials in `.env` file
   - Verify AEM URL is correct
   - Ensure you have access to the AEM instance

2. **Browser Issues**

   - Run `playwright install chromium` to install browser
   - Try running with `--headless` flag
   - Check if port 3000 is available

3. **Component Not Found**

   - Verify component names match AEM exactly
   - Check if you have permissions to add components
   - Try using different component types

4. **Navigation Errors**
   - Ensure the target path exists in AEM
   - Check folder permissions
   - Verify site structure matches expectations

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python cli.py --verbose
```

## Development

### Project Structure

```
aem-automation-agent/
├── aem_agent.py          # Main agent class
├── aem_browser.py        # Browser automation
├── prompt_parser.py      # Natural language processing
├── cli.py               # Command-line interface
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

### Adding New Features

1. **New Component Types**: Update `component_mappings` in `prompt_parser.py`
2. **New Actions**: Add action types to `PromptParser` and corresponding methods to `AEMBrowser`
3. **Enhanced Parsing**: Extend regex patterns in `prompt_parser.py`

### Testing

Run the demo workflow:

```bash
python aem_agent.py
```

This will execute a sample workflow to test all components.

## Security Considerations

- Store credentials securely in `.env` file
- Never commit credentials to version control
- Use environment-specific configurations
- Consider using secure credential management systems

## Limitations

- Currently supports Thomson Reuters AEM instance
- Limited to specific component types
- Requires manual credential management
- Browser-based automation (not API-based)

## Future Enhancements

- 🔄 API-based AEM integration
- 🔄 More component types support
- 🔄 Bulk operations
- 🔄 Template customization
- 🔄 Advanced content management
- 🔄 Integration with external content sources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for internal use at Thomson Reuters.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs with `--verbose` flag
3. Contact the development team
