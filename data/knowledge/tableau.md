---
source_id: KB-TAB-001
title: Tableau Visual Analytics and Enterprise Dashboard Design
skill: tableau
topic: Data Visualization
difficulty: Intermediate
prerequisites: Basic business intelligence and database concepts
keywords: [tableau, data visualization, lod expressions, dashboards, charts, calculated fields]
---

# Tableau Visual Analytics and Enterprise Dashboard Design

## Overview
Tableau is an enterprise visual analytics platform transforming raw data into intuitive, highly interactive dashboards. It emphasizes exploratory data visualization, visual best practices, and fast communication of complex quantitative insights.

## Core Concepts
- **Data Connections and Relationships**: Connecting to flat files and live relational databases; using the Tableau semantic layer (logical relationships vs physical joins).
- **Dimensions vs Measures**: Discrete (blue) vs Continuous (green) pills and their distinct visual effects on chart axes and headers.
- **Calculated Fields**: Basic mathematical formulas, string operations, date calculations (DATEDIFF, DATEADD), and conditional IF-THEN-ELSE expressions.
- **Level of Detail (LOD) Expressions**: FIXED, INCLUDE, and EXCLUDE expressions allowing calculations at a level of granularity different from the visualization display.
- **Table Calculations**: Running totals, percent of total, rank, and moving averages calculated along specific visual partitions and directions.
- **Dashboard Interactivity**: Action filters, highlight actions, parameters, and dynamic tooltips designed for executive end-users.

## Learning Objectives
1. Connect diverse data sources and build clean logical relationships without duplicate aggregation errors.
2. Formulate Level of Detail (LOD) calculations to compute cohort metrics and global market shares.
3. Design cohesive, accessible interactive dashboards utilizing visual hierarchy and clean design principles.
4. Implement parameter-driven charts allowing end users to toggle dimensions and metrics dynamically.

## Practice Projects
- **Global Supply Chain Logistics Dashboard**: Build a visual dashboard tracking on-time delivery rates, shipping carrier performance across regions, and delay heatmaps.
- **Cohort Retention Visualizer**: Create a Tableau dashboard utilizing FIXED LOD expressions to visualize customer cohort retention curves across quarterly sign-up cohorts.
