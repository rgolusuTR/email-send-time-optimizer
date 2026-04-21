# Excel Issue Separator

A modern React application that automatically separates Excel files by issue types. Perfect for organizing bug reports, feedback, or any categorized data.

## Features

- **Drag & Drop Upload**: Easy file upload with drag and drop support
- **Multiple File Formats**: Supports .xlsx, .xls, and .csv files
- **Automatic Issue Detection**: Automatically finds and groups issues by type
- **Interactive Results**: View detailed statistics and preview data
- **Flexible Export Options**:
  - Export as single file with multiple sheets
  - Export as separate files for each issue type
  - Include summary statistics
- **Sample Template**: Download a sample template to get started

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. Clone the repository or download the project files
2. Navigate to the project directory:
   ```bash
   cd excel-issue-separator
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
5. Open your browser and navigate to `http://localhost:5173`

## Usage

### File Requirements

Your Excel file must meet these requirements:

- Contains a column with "Issue", "Problem", or "Type" in the header
- Each row represents one issue or data point
- First row contains column headers
- File size less than 50MB

### Step-by-Step Guide

1. **Upload File**: Drag and drop your Excel file or click to browse
2. **Processing**: The app will automatically analyze your data and group issues by type
3. **Review Results**: View statistics and preview your data
4. **Export**: Choose your export format and select which issue types to include
5. **Download**: Get your organized files instantly

### Sample Data Format

| Page URL                  | Issue Type       | Description                         | Severity | Date Found |
| ------------------------- | ---------------- | ----------------------------------- | -------- | ---------- |
| https://example.com/page1 | Broken Link      | Link to external resource is broken | High     | 2024-01-15 |
| https://example.com/page2 | Missing Alt Text | Image missing alt attribute         | Medium   | 2024-01-16 |
| https://example.com/page3 | Broken Link      | Internal link returns 404           | High     | 2024-01-17 |

## Export Options

### Single File Export

- Creates one Excel file with separate sheets for each issue type
- Optional summary sheet with statistics
- Ideal for comprehensive reporting

### Multiple Files Export

- Creates separate Excel files for each issue type
- Perfect for distributing specific issues to different teams
- Cleaner organization for large datasets

## Technical Details

### Built With

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **SheetJS (xlsx)** - Excel file processing
- **FileSaver.js** - Client-side file downloads

### Project Structure

```
src/
├── components/          # React components
│   ├── FileUpload.tsx   # File upload interface
│   ├── ProcessingStatus.tsx # Loading state
│   ├── ResultsView.tsx  # Results display
│   └── ExportPanel.tsx  # Export options
├── lib/                 # Utility libraries
│   ├── excelProcessor.ts # Excel file processing
│   └── exportUtils.ts   # Export functionality
├── types/               # TypeScript type definitions
│   └── index.ts
├── App.tsx             # Main application component
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Performance

- Handles files up to 50MB
- Processes thousands of rows efficiently
- Client-side processing (no server required)
- Responsive design for all screen sizes

## Troubleshooting

### Common Issues

**File not processing:**

- Ensure your file has a column containing "Issue", "Problem", or "Type"
- Check that the file is not corrupted
- Verify file size is under 50MB

**Export not working:**

- Make sure you have selected at least one issue type
- Check browser's download settings
- Try a different browser if issues persist

**Performance issues:**

- Large files may take longer to process
- Close other browser tabs to free up memory
- Consider splitting very large files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or feature requests, please create an issue in the project repository.
