import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Link,
  Box,
  Typography,
} from "@mui/material";
import {
  OpenInNew as OpenInNewIcon,
  BugReport as BugIcon,
} from "@mui/icons-material";
import { BrokenLink } from "../types/types";

interface DataTableProps {
  data: BrokenLink[];
}

export const DataTable: React.FC<DataTableProps> = ({ data }) => {
  const getPriorityColor = (score?: number) => {
    if (!score) return "default";
    if (score >= 20) return "error";
    if (score >= 10) return "warning";
    if (score >= 5) return "info";
    return "success";
  };

  const getPriorityLabel = (score?: number) => {
    if (!score) return "Low";
    if (score >= 20) return "Critical";
    if (score >= 10) return "High";
    if (score >= 5) return "Medium";
    return "Low";
  };

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell>Page Title</TableCell>
            <TableCell>URL</TableCell>
            <TableCell align="center">Broken Links</TableCell>
            <TableCell align="center">Clicks</TableCell>
            <TableCell align="center">Page Level</TableCell>
            <TableCell align="center">Page Views</TableCell>
            <TableCell align="center">Priority</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, index) => (
            <TableRow key={index} hover>
              <TableCell>
                <Box sx={{ maxWidth: 300 }}>
                  <Typography variant="body2" noWrap title={row.title}>
                    {row.title}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Box sx={{ maxWidth: 250 }}>
                  <Typography variant="body2" noWrap title={row.url}>
                    {row.url}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell align="center">
                <Chip
                  icon={<BugIcon />}
                  label={row.broken_links}
                  size="small"
                  color={
                    row.broken_links > 5
                      ? "error"
                      : row.broken_links > 2
                      ? "warning"
                      : "default"
                  }
                />
              </TableCell>
              <TableCell align="center">{row.clicks}</TableCell>
              <TableCell align="center">{row.page_level}</TableCell>
              <TableCell align="center">{row.page_views}</TableCell>
              <TableCell align="center">
                <Chip
                  label={getPriorityLabel(row.priority_score)}
                  size="small"
                  color={getPriorityColor(row.priority_score)}
                  variant="outlined"
                />
              </TableCell>
              <TableCell align="center">
                <Link
                  href={row.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ display: "inline-flex", alignItems: "center" }}
                >
                  <OpenInNewIcon fontSize="small" />
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {data.length === 0 && (
        <Box sx={{ p: 3, textAlign: "center" }}>
          <Typography variant="body2" color="text.secondary">
            No broken links data available
          </Typography>
        </Box>
      )}
    </TableContainer>
  );
};
