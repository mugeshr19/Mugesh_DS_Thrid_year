# Academic Project Report Deliverables Package

**Project Title:** 25. Real-Time Traffic Congestion Predictive Modeling Using Live IoT Sensor Stream Analytics  
**Institution:** Sri Eshwar College of Engineering (An Autonomous Institution, Affiliated to Anna University, Chennai)  
**Department:** Computer Science and Engineering  
**Candidate Name:** SAI KRISHNAN S  
**Register Number:** 722824104206  
**Degree:** Master of Engineering in Computer Science and Engineering  
**Supervisor:** Dr. K. SURESH KUMAR, Associate Professor, Department of Computer Science and Engineering  
**Academic Year:** 2026 – 2027  

---

## 📁 Package Contents

This folder (`Report_Deliverables/`) contains all verified final project report documents and associated assets:

### 1. Primary Deliverables
- **`DS_Report_Sai_24CS206.docx`** (~3.09 MB)
  - Complete, formatted academic project report in Microsoft Word format.
  - Follows strict academic formatting: Times New Roman typography, 1.25" left margin, 1.0" top/bottom/right margins, black-and-white bordered tables, formal front matter, Chapters 1 to 7, genuine IEEE-style references, and Appendices A–C.
- **`DS_Report_Sai_24CS206.pdf`** (~1.74 MB, 47 Pages)
  - Authentic PDF generated directly via Microsoft Word COM automation (`win32com.client`).
  - Matches the layout, pagination, embedded high-resolution figures, headers, and footers of the Word document exactly.

---

### 2. Embedded Figures & Diagrams (`figures/`)
All figures referenced and embedded within the report are archived here in high-resolution PNG format:
- `system_architecture_diagram.png` (Figure 3.1: Overall Multi-Layer System Architecture)
- `traffic_speed_distribution.png` (Figure 4.1: Distribution of Space Mean Speeds)
- `hourly_traffic_patterns.png` (Figure 4.2: Diurnal Traffic Dynamics: Mean Hourly Flow and Speed Curves)
- `speed_vs_volume_fundamental_diagram.png` (Figure 4.3: Greenshields Fundamental Diagram of Traffic Flow)
- `congestion_level_distribution.png` (Figure 4.4: Ground-Truth HCM Level of Service Class Distribution)
- `sensor_geographic_topology.png` (Figure 4.5: Geographic Sensor Node Coordinate Scatter)
- `model_comparison_metrics.png` (Figure 6.1: Comparative Test Accuracy and Macro F1 Across Models)
- `model_confusion_matrix.png` (Figure 6.2: Multi-Class Confusion Matrix for HistGradientBoosting Classifier)
- `feature_importance.png` (Figure 6.3: Top 10 Permutation Feature Importances for 15-Minute Congestion Classification)
- `regression_residuals_analysis.png` (Figure 6.4: Residual Error Distribution for Speed Forecasting Model)
- `dashboard_overview_screenshot.png` (Figure B.1: Overview Monitoring Screen)
- `dashboard_map_screenshot.png` (Figure B.2: Interactive Leaflet OpenStreetMap Sensor Node Visualization)
- `dashboard_monitoring_screenshot.png` (Figure B.3: Live IoT Sensor Telemetry Stream Table)
- `dashboard_prediction_screenshot.png` (Figure B.4: Real-Time Machine Learning Congestion Forecasting Screen)

---

### 3. Institutional Assets (`assets/`)
- `Image21.jpg`: Official College Emblem / Logo.
- `college_header.png`: Institutional Banner Header.

---

### 4. Machine Learning & Statistical Metrics (`metrics/`)
- `classification_report.json`: Precision, Recall, F1-Score breakdown across HCM LOS congestion classes.
- `regression_metrics.json`: MAE, MSE, RMSE, R² scores for numerical speed forecasting.
- `model_comparison.json`: Benchmarking HistGradientBoosting against Random Forest, Decision Tree, and Logistic Regression baselines.

---

### 5. Research & System Documentation (`docs/`)
- `docs/METHODOLOGY.md`: Detailed traffic flow theory (Greenshields equation, HCM LOS levels) and ML methodology.
- `docs/ARCHITECTURE.md`: High-level system design and data flow specifications.
- `docs/DATABASE_SCHEMA.md`: SQLite WAL relational database schema and entity descriptions.
