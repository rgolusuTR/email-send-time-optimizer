import { useState } from "react";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Box,
} from "@mui/material";
import { MainLayout } from "./components/layout/MainLayout";
import { AnalysisTypeSelector } from "./components/analysis/AnalysisTypeSelector";
import { FileUpload } from "./components/upload/FileUpload";
import { FilterPanel } from "./components/filters/FilterPanel";
import { ResultsDisplay } from "./components/results/ResultsDisplay";
import { HistoryPanel } from "./components/history/HistoryPanel";
import { SettingsPanel } from "./components/settings/SettingsPanel";
import { useAppStore } from "./store/useAppStore";
import { parseFile, processEmailData, filterData } from "./utils/dataParser";
import { validateEmailData } from "./utils/validation";
import { performAnalysis } from "./utils/analysisEngine";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
  },
});

function App() {
  const [historyOpen, setHistoryOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const {
    currentFile,
    currentData,
    currentResults,
    analysisType,
    filters,
    isLoading,
    error,
    setCurrentFile,
    setCurrentData,
    setCurrentResults,
    setAnalysisType,
    setFilters,
    setLoading,
    setError,
  } = useAppStore();

  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      setError(null);
      setCurrentFile(file);

      // Reset filters to "All" when uploading a new file
      const defaultFilters = {
        businessUnit: "All",
        organizationType: "All",
        campaignType: "All",
        timezone: undefined,
      };
      setFilters(defaultFilters);

      // Parse file
      const rawData = await parseFile(file);

      // Validate data
      const validation = validateEmailData(rawData);

      if (!validation.isValid) {
        setError(validation.errors.join(". "));
        setLoading(false);
        return;
      }

      // Show warnings if any
      if (validation.warnings.length > 0) {
        console.warn("Data warnings:", validation.warnings);
      }

      // Process data
      const processed = processEmailData(rawData);

      if (processed.length === 0) {
        setError("No valid data found in the file after processing.");
        setLoading(false);
        return;
      }

      setCurrentData(processed);

      // Perform initial analysis with default filters
      const filtered = filterData(processed, defaultFilters);
      const results = performAnalysis(filtered, analysisType, defaultFilters);
      setCurrentResults(results);

      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process file");
      setLoading(false);
    }
  };

  const handleAnalysisTypeChange = (newType: typeof analysisType) => {
    setAnalysisType(newType);

    if (currentData.length > 0) {
      try {
        const filtered = filterData(currentData, filters);
        console.log(
          `Filtered data count: ${filtered.length} out of ${currentData.length}`
        );
        const results = performAnalysis(filtered, newType, filters);
        console.log(
          `Analysis complete. Total records in metadata: ${results.metadata.totalRecords}`
        );
        setCurrentResults(results);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Analysis failed");
      }
    }
  };

  const handleFilterChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
  };

  const handleAnalyze = () => {
    if (currentData.length > 0) {
      try {
        setError(null);
        const filtered = filterData(currentData, filters);
        console.log(
          `Filtered data count: ${filtered.length} out of ${currentData.length}`
        );

        if (filtered.length === 0) {
          setError(
            "No data available for analysis with the selected filters. Please adjust your filter selections."
          );
          setCurrentResults(null);
          return;
        }

        const results = performAnalysis(filtered, analysisType, filters);
        console.log(
          `Analysis complete. Total records in metadata: ${results.metadata.totalRecords}`
        );
        setCurrentResults(results);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Analysis failed");
        setCurrentResults(null);
      }
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MainLayout
        onHistoryClick={() => setHistoryOpen(true)}
        onSettingsClick={() => setSettingsOpen(true)}
      >
        <Container maxWidth="xl" sx={{ py: 4 }}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
            {/* Analysis Type Selector */}
            <AnalysisTypeSelector
              value={analysisType}
              onChange={handleAnalysisTypeChange}
            />

            {/* File Upload */}
            <FileUpload
              onFileUpload={handleFileUpload}
              isLoading={isLoading}
              currentFile={currentFile}
            />

            {/* Filters */}
            {currentData.length > 0 && (
              <FilterPanel
                data={currentData}
                filters={filters}
                onChange={handleFilterChange}
                onAnalyze={handleAnalyze}
              />
            )}

            {/* Error Display */}
            {error && (
              <Box
                sx={{
                  p: 2,
                  bgcolor: "error.light",
                  color: "error.contrastText",
                  borderRadius: 1,
                }}
              >
                {error}
              </Box>
            )}

            {/* Results */}
            {currentResults && !isLoading && (
              <ResultsDisplay results={currentResults} data={currentData} />
            )}
          </Box>
        </Container>
      </MainLayout>

      {/* History Panel */}
      <HistoryPanel open={historyOpen} onClose={() => setHistoryOpen(false)} />

      {/* Settings Panel */}
      <SettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </ThemeProvider>
  );
}

export default App;
