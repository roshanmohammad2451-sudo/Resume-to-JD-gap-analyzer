---
source_id: KB-AWS-001
title: Amazon Web Services (AWS) Core Cloud Infrastructure
skill: aws
topic: Cloud Computing
difficulty: Intermediate
prerequisites: Basic networking and systems administration
keywords: [aws, amazon web services, cloud, ec2, s3, iam, lambda, rds, vpc, cloudwatch]
---

# Amazon Web Services (AWS) Core Cloud Infrastructure

## Overview
Amazon Web Services (AWS) is the world's most widely adopted cloud platform, offering over 200 fully featured services from data centers globally. Core cloud competency focuses on secure identity, compute, storage, database, and networking primitives.

## Core Concepts
- **Identity and Access Management (IAM)**: Principle of least privilege; IAM users, groups, roles, policies (JSON documents), and temporary credentials via STS.
- **Compute Services**: Amazon EC2 (virtual server instances, AMI selection, instance families), Auto Scaling Groups, and AWS Lambda (serverless event-driven execution).
- **Storage Solutions**: Amazon S3 (object storage, buckets, lifecycle rules, presigned URLs) and Amazon EBS (persistent block storage volumes for EC2).
- **Managed Databases**: Amazon RDS (managed PostgreSQL/MySQL with automated backups, multi-AZ failover, read replicas) and DynamoDB (NoSQL key-value store).
- **Networking (VPC)**: Virtual Private Cloud (VPC), public and private subnets, Route Tables, Internet Gateways, NAT Gateways, and Security Groups (stateful virtual firewalls).
- **Monitoring and Logging**: CloudWatch metrics, alarms, and CloudWatch Logs for application tracing and alerting.

## Learning Objectives
1. Design a secure VPC architecture separating public-facing load balancers from private database instances.
2. Formulate granular IAM policies granting least-privilege permissions to applications and services.
3. Deploy stateless containerized or serverless applications utilizing EC2 or AWS Lambda connected to Amazon RDS.
4. Manage static assets and file uploads using secure Amazon S3 bucket policies and presigned URLs.

## Practice Projects
- **Secure 2-Tier Web Architecture**: Build a cloud architecture pattern with a public subnet hosting an Application Load Balancer and private subnets hosting EC2 backend instances and an RDS PostgreSQL database.
- **Serverless Image Processing Pipeline**: Configure an S3 bucket event triggering an AWS Lambda function that extracts image metadata and writes records to a database.
