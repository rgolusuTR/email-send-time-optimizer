// Dashboard JavaScript
class SiteimproveDashboard {
  constructor() {
    this.currentFilters = {
      websites: [],
      reportTypes: [],
      startDate: null,
      endDate: null,
      period: "daily",
    };
    this.charts = {};
    this.currentPage = 1;
    this.searchTerm = "";

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.initializeDatePicker();
    this.loadInitialData();
  }

  setupEventListeners() {
    // Filter controls
    $("#applyFilters").on("click", () => this.applyFilters());
    $("#refreshData").on("click", () => this.refreshData());
    $("#exportDashboard").on("click", () => this.exportDashboard());

    // Search functionality
    $("#searchButton").on("click", () => this.performSearch());
    $("#searchInput").on("keypress", (e) => {
      if (e.which === 13) this.performSearch();
    });

    // Pagination
    $(document).on("click", ".page-link", (e) => {
      e.preventDefault();
      const page = $(e.target).data("page");
      if (page) this.loadDetailedData(page);
    });

    // View all details
    $("#viewAllDetails").on("click", () => this.scrollToDetailedData());
  }

  initializeDatePicker() {
    flatpickr("#dateRange", {
      mode: "range",
      dateFormat: "Y-m-d",
      defaultDate: [
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        new Date(),
      ],
      onChange: (selectedDates) => {
        if (selectedDates.length === 2) {
          this.currentFilters.startDate = selectedDates[0];
          this.currentFilters.endDate = selectedDates[1];
        }
      },
    });
  }

  async loadInitialData() {
    try {
      this.showLoading(true);

      // Load websites
      await this.loadWebsites();

      // Load initial dashboard data
      await this.loadDashboardData();
    } catch (error) {
      this.showError("Failed to load initial data: " + error.message);
    } finally {
      this.showLoading(false);
    }
  }

  async loadWebsites() {
    try {
      const response = await fetch("/api/websites");
      const websites = await response.json();

      const websiteSelect = $("#websiteFilter");
      websiteSelect.empty();

      websites.forEach((website) => {
        websiteSelect.append(
          `<option value="${website.id}">${website.name}</option>`
        );
      });

      // Select all by default
      websiteSelect.val(websites.map((w) => w.id));
      this.currentFilters.websites = websites.map((w) => w.id);
    } catch (error) {
      console.error("Error loading websites:", error);
    }
  }

  async loadDashboardData() {
    try {
      this.showLoading(true);

      const params = this.buildFilterParams();
      const response = await fetch(`/api/dashboard-data?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      this.updateSummaryStats(data.summary_stats);
      this.updateCharts(data);
      this.updateRecentIssues(data.detailed_data);
      this.loadDetailedData(1);
    } catch (error) {
      this.showError("Failed to load dashboard data: " + error.message);
    } finally {
      this.showLoading(false);
    }
  }

  buildFilterParams() {
    const params = new URLSearchParams();

    // Websites
    this.currentFilters.websites.forEach((id) => {
      params.append("websites[]", id);
    });

    // Report types
    this.currentFilters.reportTypes.forEach((type) => {
      params.append("report_types[]", type);
    });

    // Date range
    if (this.currentFilters.startDate) {
      params.append(
        "start_date",
        this.formatDate(this.currentFilters.startDate)
      );
    }
    if (this.currentFilters.endDate) {
      params.append("end_date", this.formatDate(this.currentFilters.endDate));
    }

    // Period
    params.append("period", this.currentFilters.period);

    return params.toString();
  }

  formatDate(date) {
    return date.toISOString().split("T")[0];
  }

  updateSummaryStats(stats) {
    $("#totalReports").text(this.formatNumber(stats.total_reports || 0));
    $("#totalMisspellings").text(
      this.formatNumber(stats.total_misspellings || 0)
    );
    $("#totalWordsToReview").text(
      this.formatNumber(stats.total_words_to_review || 0)
    );
    $("#totalPagesAffected").text(
      this.formatNumber(stats.total_pages_affected || 0)
    );

    // Add animation
    $(".stats-card").addClass("fade-in");
  }

  formatNumber(num) {
    return new Intl.NumberFormat().format(num);
  }

  updateCharts(data) {
    // Update trend chart
    if (data.trend_data) {
      this.updateTrendChart(data.trend_data);
    }

    // Update top words chart
    if (data.top_words) {
      this.updateTopWordsChart(data.top_words);
    }

    // Update language distribution chart
    if (data.language_distribution) {
      this.updateLanguageChart(data.language_distribution);
    }
  }

  updateTrendChart(data) {
    const ctx = document.getElementById("trendChart").getContext("2d");

    if (this.charts.trend) {
      this.charts.trend.destroy();
    }

    this.charts.trend = new Chart(ctx, {
      type: "line",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Misspellings Trend Over Time",
          },
          legend: {
            position: "top",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Count",
            },
          },
          x: {
            title: {
              display: true,
              text: "Date",
            },
          },
        },
        interaction: {
          intersect: false,
          mode: "index",
        },
      },
    });
  }

  updateTopWordsChart(data) {
    const ctx = document.getElementById("topWordsChart").getContext("2d");

    if (this.charts.topWords) {
      this.charts.topWords.destroy();
    }

    this.charts.topWords = new Chart(ctx, {
      type: "bar",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Top Misspelled Words",
          },
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Pages Affected",
            },
          },
          x: {
            title: {
              display: true,
              text: "Words",
            },
          },
        },
      },
    });
  }

  updateLanguageChart(data) {
    const ctx = document.getElementById("languageChart").getContext("2d");

    if (this.charts.language) {
      this.charts.language.destroy();
    }

    this.charts.language = new Chart(ctx, {
      type: "doughnut",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Language Distribution",
          },
          legend: {
            position: "bottom",
          },
        },
      },
    });
  }

  updateRecentIssues(detailedData) {
    const container = $("#recentIssues");
    container.empty();

    if (!detailedData || !detailedData.data || detailedData.data.length === 0) {
      container.html('<p class="text-muted">No recent issues found.</p>');
      return;
    }

    const recentItems = detailedData.data.slice(0, 5);

    recentItems.forEach((item) => {
      const issueHtml = `
                <div class="border-bottom pb-2 mb-2">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <strong>${item.word || "N/A"}</strong>
                            <span class="badge bg-secondary ms-2">${
                              item.type
                            }</span>
                        </div>
                        <small class="text-muted">${
                          item.pages || 0
                        } pages</small>
                    </div>
                    <div class="text-muted small">
                        Suggestion: ${item.suggestion || "N/A"} | 
                        Website: ${item.website || "N/A"}
                    </div>
                </div>
            `;
      container.append(issueHtml);
    });
  }

  async loadDetailedData(page = 1) {
    try {
      const params = this.buildFilterParams();
      params.append("page", page);
      params.append("per_page", 50);

      if (this.searchTerm) {
        params.append("search", this.searchTerm);
      }

      const response = await fetch(`/api/detailed-data?${params}`);
      const data = await response.json();

      this.updateDetailedTable(data);
      this.updatePagination(data);
      this.currentPage = page;
    } catch (error) {
      this.showError("Failed to load detailed data: " + error.message);
    }
  }

  updateDetailedTable(data) {
    const tbody = $("#detailedDataBody");
    tbody.empty();

    if (!data.data || data.data.length === 0) {
      tbody.append(`
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        No data found for the selected filters.
                    </td>
                </tr>
            `);
      return;
    }

    data.data.forEach((item) => {
      const row = `
                <tr>
                    <td><span class="badge bg-info">${item.type}</span></td>
                    <td><strong>${item.word || "N/A"}</strong></td>
                    <td>${item.suggestion || "N/A"}</td>
                    <td>${item.language || "N/A"}</td>
                    <td>${this.formatDate(item.first_detected) || "N/A"}</td>
                    <td>${item.pages || 0}</td>
                    <td>${item.website || "N/A"}</td>
                    <td>${this.formatDate(item.report_date) || "N/A"}</td>
                </tr>
            `;
      tbody.append(row);
    });
  }

  updatePagination(data) {
    const pagination = $("#pagination");
    pagination.empty();

    if (data.total_pages <= 1) return;

    // Previous button
    const prevDisabled = data.page <= 1 ? "disabled" : "";
    pagination.append(`
            <li class="page-item ${prevDisabled}">
                <a class="page-link" href="#" data-page="${
                  data.page - 1
                }">Previous</a>
            </li>
        `);

    // Page numbers
    const startPage = Math.max(1, data.page - 2);
    const endPage = Math.min(data.total_pages, data.page + 2);

    for (let i = startPage; i <= endPage; i++) {
      const active = i === data.page ? "active" : "";
      pagination.append(`
                <li class="page-item ${active}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `);
    }

    // Next button
    const nextDisabled = data.page >= data.total_pages ? "disabled" : "";
    pagination.append(`
            <li class="page-item ${nextDisabled}">
                <a class="page-link" href="#" data-page="${
                  data.page + 1
                }">Next</a>
            </li>
        `);
  }

  applyFilters() {
    // Get selected values
    this.currentFilters.websites = $("#websiteFilter").val() || [];
    this.currentFilters.reportTypes = $("#reportTypeFilter").val() || [];
    this.currentFilters.period = $("#periodFilter").val();

    // Get date range from flatpickr
    const dateRange = $("#dateRange")[0]._flatpickr.selectedDates;
    if (dateRange.length === 2) {
      this.currentFilters.startDate = dateRange[0];
      this.currentFilters.endDate = dateRange[1];
    }

    // Reset pagination
    this.currentPage = 1;
    this.searchTerm = "";
    $("#searchInput").val("");

    // Reload data
    this.loadDashboardData();
  }

  refreshData() {
    this.loadDashboardData();
  }

  performSearch() {
    this.searchTerm = $("#searchInput").val().trim();
    this.currentPage = 1;
    this.loadDetailedData(1);
  }

  scrollToDetailedData() {
    $("html, body").animate(
      {
        scrollTop: $("#detailedDataTable").offset().top - 100,
      },
      500
    );
  }

  async exportDashboard() {
    try {
      const exportBtn = $("#exportDashboard");
      const originalText = exportBtn.html();

      exportBtn
        .prop("disabled", true)
        .html('<i class="fas fa-spinner fa-spin me-1"></i>Exporting...');

      const params = this.buildFilterParams();
      const response = await fetch(`/api/export?${params}`);

      if (!response.ok) {
        throw new Error("Export failed");
      }

      // Download the file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `siteimprove_dashboard_export_${
        new Date().toISOString().split("T")[0]
      }.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      this.showSuccess("Dashboard exported successfully!");
    } catch (error) {
      this.showError("Export failed: " + error.message);
    } finally {
      const exportBtn = $("#exportDashboard");
      exportBtn
        .prop("disabled", false)
        .html('<i class="fas fa-download me-1"></i>Export to Excel');
    }
  }

  showLoading(show) {
    if (show) {
      $("#loadingIndicator").show();
      $("#summaryStats, .row").not("#loadingIndicator").hide();
    } else {
      $("#loadingIndicator").hide();
      $("#summaryStats, .row").not("#loadingIndicator").show();
    }
  }

  showError(message) {
    const alert = $("#errorAlert");
    $("#errorMessage").text(message);
    alert.removeClass("show").addClass("show").show();

    // Auto-hide after 5 seconds
    setTimeout(() => {
      alert.removeClass("show");
    }, 5000);
  }

  showSuccess(message) {
    // Create a temporary success alert
    const successAlert = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

    $(successAlert).insertAfter(".border-bottom").delay(3000).fadeOut();
  }
}

// Initialize dashboard when document is ready
$(document).ready(function () {
  window.dashboard = new SiteimproveDashboard();
});
