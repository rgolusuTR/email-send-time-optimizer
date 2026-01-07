# Email Send Time Optimizer

A modern React application for analyzing email campaign data and determining optimal send times based on historical performance metrics.

## Features

- **Multiple Analysis Types**

  - Best Practices: Industry-standard recommendations
  - Historical Data: Your past campaign performance
  - Combined: Blend of both approaches

- **Advanced Filtering**

  - Filter by Business Unit, Organization Type, and Campaign Type
  - Optional timezone support for global campaigns

- **Large File Support**

  - Handles datasets with 60,000+ rows
  - Efficient CSV and Excel file parsing
  - Drag-and-drop file upload

- **Comprehensive Analytics**

  - Top 3 recommended send times
  - Performance visualizations by day and time
  - Open rates, click rates, and engagement metrics

- **Export Capabilities**
  - PDF reports
  - Excel spreadsheets
  - CSV data files
  - JSON format

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:

```bash
cd email-send-time-optimizer
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

4. Open your browser to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage

### Data Format

Your CSV or Excel file should include the following columns:

**Required:**

- Business Unit
- Organization Type
- Campaign Type
- Send Date (format: MM/DD/YYYY or YYYY-MM-DD)
- Send Time (format: HH:MM AM/PM or HH:MM)
- Open Rate (percentage)

**Optional:**

- Click Rate (percentage)
- Unsubscribe Rate (percentage)
- Bounce Rate (percentage)

### Workflow

1. **Select Analysis Type**: Choose between Best Practices, Historical Data, or Combined analysis
2. **Upload Data**: Drag and drop or select your CSV/Excel file
3. **Apply Filters**: Refine your analysis by filtering the data
4. **View Results**: See the top 3 recommended send times with performance metrics
5. **Export**: Download results in your preferred format

## Technology Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for UI components
- **Recharts** for data visualization
- **Papa Parse** for CSV parsing
- **XLSX** for Excel file handling
- **jsPDF** for PDF generation
- **Zustand** for state management
- **Vite** for build tooling

## Project Structure

```
email-send-time-optimizer/
├── src/
│   ├── components/
│   │   ├── analysis/        # Analysis type selector
│   │   ├── filters/         # Filter controls
│   │   ├── history/         # Analysis history panel
│   │   ├── layout/          # Main layout components
│   │   ├── results/         # Results display and charts
│   │   ├── settings/        # Settings panel
│   │   └── upload/          # File upload component
│   ├── store/               # Zustand state management
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   │   ├── analysisEngine.ts    # Core analysis logic
│   │   ├── dataParser.ts        # Data parsing utilities
│   │   ├── exportUtils.ts       # Export functionality
│   │   └── validation.ts        # Data validation
│   ├── App.tsx              # Main application component
│   └── main.tsx             # Application entry point
├── public/                  # Static assets
└── package.json            # Dependencies and scripts
```

## Features in Detail

### Analysis Engine

The analysis engine supports three modes:

1. **Best Practices**: Uses industry-standard optimal send times
2. **Historical**: Analyzes your actual campaign performance data
3. **Combined**: Weights both approaches for balanced recommendations

### Performance Optimization

- Efficient data processing for large datasets
- Memoized calculations to prevent unnecessary re-renders
- Lazy loading of components
- Optimized chart rendering

### Data Validation

- Validates required columns on file upload
- Checks data types and formats
- Provides clear error messages for invalid data
- Handles missing or malformed data gracefully

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

This is a Thomson Reuters internal project. For questions or issues, please contact the development team.

## License

Proprietary - Thomson Reuters

## Version History

- **v1.0.0** (2026-01-07): Initial release
  - Core analysis functionality
  - Multiple export formats
  - Responsive design
  - Large file support
