# DATAHUB V16.0 RC1

## Release candidate scope
- API service
- repository boundary
- policy engine boundary
- tenant isolation
- governed work lifecycle
- audit
- outbox/event boundary
- PostgreSQL production schema
- Control Center shell
- automated tests
- Docker baseline

## Critical production substitutions
The RC remains a runnable reference implementation. Before a production release:
- replace in-memory repository with PostgreSQL repository;
- replace development identity headers with verified OIDC/OAuth2;
- make audit/outbox transactional;
- connect outbox to a real broker;
- configure secrets, TLS, monitoring and backups;
- execute security, load, recovery and rollback tests.

## Definition of release candidate
The architecture and contracts are frozen enough for implementation hardening; production readiness still requires evidence from the listed gates.
