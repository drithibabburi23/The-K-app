# Deployment Readiness

Deployment is not complete. The repository does not yet contain a central backend, database, Firebase platform configuration, durable media storage, or an implemented M5 service.

## Required Before Release

1. Implement and deploy the authenticated central API and database.
2. Recover or replace the missing M5 marketplace implementation.
3. Configure M2 and M3 behind authenticated backend adapters.
4. Add production secrets through the deployment platform, never source files.
5. Replace M3 debug mode and local public output storage.
6. Add Firebase configuration for each target Flutter platform.
7. Add durable offline storage and idempotent draft synchronization.
8. Run the complete test and release checklist in [TESTING.md](TESTING.md).

## Configuration Placeholders

- Flutter: central API base URL and environment-specific Firebase configuration.
- M2: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_TRANSCRIPTION_MODEL`.
- M3: `REMOVE_BACKGROUND` plus authenticated durable media storage settings to be added.
- M4: database, authentication, and service URLs to be defined with the central backend.
- M5: pricing and marketplace service configuration after its source is recovered.

No production URL or credential is configured in this workspace.