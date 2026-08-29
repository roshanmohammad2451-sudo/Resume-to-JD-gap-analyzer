---
source_id: KB-PBI-001
title: Microsoft Power BI Business Intelligence and Data Modeling
skill: power bi
topic: Business Intelligence & Data Visualization
difficulty: Intermediate
prerequisites: Excel and relational data concepts
keywords: [power bi, ms power bi, dax, power query, data modeling, dashboards, bi, reports]
---

# Microsoft Power BI Business Intelligence and Data Modeling

## Overview
Microsoft Power BI is a suite of business analytics tools that deliver insights across organizations. It enables connecting to hundreds of data sources, shaping data with Power Query, establishing relational data models, and publishing interactive dashboards.

## Core Concepts
- **Power Query (M Language)**: Extracting, transforming, and loading (ETL) data; cleaning unpivoted columns, setting data types, and merging multiple source queries.
- **Data Modeling (Star Schema)**: Organizing tables into Fact tables (transactions, events) and Dimension tables (customers, dates, products) with 1-to-many relationships.
- **DAX (Data Analysis Expressions)**: Authoring calculated columns and measures; understanding row context vs filter context; core functions: CALCULATE, FILTER, ALL, RELATED, SUMX.
- **Time Intelligence in DAX**: Calculating Year-to-Date (TOTALYTD), Same Period Last Year (SAMEPERIODLASTYEAR), and moving averages over custom date dimensions.
- **Interactive Visualization**: Designing cards, bar charts, decomposition trees, and matrix tables connected through cross-filtering and drill-through actions.
- **Row-Level Security (RLS)**: Defining security roles within Power BI Desktop to restrict data access based on user credentials.

## Learning Objectives
1. Perform robust ETL operations using Power Query to ingest clean data into the Power BI engine.
2. Build efficient Star Schema data models avoiding bi-directional relationships and circular dependencies.
3. Formulate DAX measures utilizing `CALCULATE` to evaluate custom business KPIs under dynamic filter contexts.
4. Construct interactive, user-friendly dashboards equipped with drill-through pages, bookmarks, and slicers.

## Practice Projects
- **Retail Sales & Margin BI Report**: Ingest multiple sales and inventory CSVs, model a Star Schema with a standard calendar table, write DAX measures for Gross Margin % and YoY Growth, and build an interactive multi-page dashboard.
- **Customer Lifetime Value Model**: Create DAX measures tracking repeat purchase rates, average tenure, and cohort analysis across historical customer transactions.
