---
source_id: KB-PAN-001
title: Pandas Library for Data Analysis and Manipulation
skill: pandas
topic: Data Science & Analytics
difficulty: Beginner to Intermediate
prerequisites: Python fundamentals
keywords: [pandas, dataframe, series, data cleaning, aggregation, groupby, tabular data]
---

# Pandas Library for Data Analysis and Manipulation

## Overview
Pandas is the core Python data analysis and manipulation library. It provides fast, flexible, and expressive data structures (Series and DataFrame) designed to make working with structured tabular and time-series data intuitive.

## Core Concepts
- **Core Data Structures**: `Series` (1D labeled homogeneous array) and `DataFrame` (2D labeled tabular structure with columns of potentially different types).
- **Data Ingestion and Export**: Reading and writing data formats including CSV (`read_csv`), Excel (`read_excel`), JSON (`read_json`), and Parquet (`read_parquet`).
- **Indexing and Selection**: Positional indexing (`iloc`), label-based indexing (`loc`), and boolean masking for conditional filtering.
- **Handling Missing Values**: Detecting null values (`isna`), filling missing data (`fillna`), and dropping invalid rows (`dropna`).
- **Data Transformation and Feature Engineering**: Column calculations, vector operations, mapping dictionary values, and applying custom functions (`apply`, `map`).
- **Aggregation and Grouping**: GroupBy split-apply-combine workflows, pivot tables, cross-tabulations, and calculating window/rolling metrics.
- **Merging and Reshaping**: Combining DataFrames using `merge` (relational joins), `concat` (stacking), `melt` (unpivoting), and `pivot`.

## Learning Objectives
1. Load raw heterogeneous datasets and conduct exploratory data cleaning (handling nulls, correcting data types).
2. Perform vectorized data transformations and filtering without inefficient Python loops.
3. Compute business summaries across categorical dimensions using `groupby` and aggregate functions.
4. Merge relational tables on common keys to produce unified analytical tables.

## Practice Projects
- **Customer Churn Data Pipeline**: Load a raw customer usage CSV, clean erroneous strings, impute missing values, engineer usage change metrics, and export cleaned features.
- **Sales Performance Aggregator**: Process 50,000 retail transaction records to output monthly branch revenue, top-performing product categories, and average basket sizes.
