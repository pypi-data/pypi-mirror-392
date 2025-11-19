*********
Changelog
*********
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)

===================
[0.11] - 2025-11-17
===================

Fixed
=====
  - Fixed DSQL connection error where schema search_path was incorrectly set using parameterized queries instead of proper SQL identifier formatting

===================
[0.10] - 2025-11-15
===================

Added
=====
  - AWS DSQL connection support with IAM authentication via ``create_dsql_connection()``
  - Automatic SSL/TLS configuration optimized for DSQL clusters
  - Configurable PostgreSQL schema search_path (defaults to 'public')
  - psycopg 3.x compatibility with version-specific SSL negotiation
  - BSD 3-Clause license
  - Comprehensive DSQL documentation in README.rst


Changed
=======
  - Made schema parameter configurable in DSQL connections to support multi-schema databases
  - Updated setup.cfg with license metadata and classifier

==================
[0.5] - 2025-09-05
==================

Created
=======
  - Initial project created.
