# KarigarConnect

This workspace contains independent member submissions and an isolated integration target under `karigar_connect/`.

## Current State

The audit is complete. Read:

- [INTEGRATION_AUDIT.md](INTEGRATION_AUDIT.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [INTEGRATION_CONTRACT.md](INTEGRATION_CONTRACT.md)

The new Flutter application is a buildable starter with role selection, an artisan draft flow, local catalog extraction, and repository/service boundaries. It does not claim live authentication, backend persistence, image processing, voice transcription, pricing, marketplace, or admin behavior until those missing integrations are implemented.

## Run the Flutter App

```powershell
Set-Location .\karigar_connect
flutter pub get
flutter run
```

Validate it with:

```powershell
flutter analyze
flutter test
```

## Member Services

M2 can be run from `member-2-main` with the dependencies in its `pyproject.toml`. M3 can be run from `m3-main` with `requirements.txt`. Their verified endpoints and required configuration are documented in [INTEGRATION_CONTRACT.md](INTEGRATION_CONTRACT.md).

Do not place real API keys in this workspace. M2 uses `OPENAI_API_KEY` through environment configuration only.