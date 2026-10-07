# OSINT Pipeline Implementation Boundary

Implement the reviewed `specs/002-osint-data-pipeline/` plan here. The first
milestone is an offline fixture importer, not a scraper or a new Airflow stack.

The existing private OSINT runner remains the eventual collection command
surface. Integrate through a reviewed adapter and the shared evidence contract;
do not vendor private code, case files, or credentials into this public fork.
