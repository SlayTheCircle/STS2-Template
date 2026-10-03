# __MOD_ID__ · __MOD_SUMMARY_EN__

[简体中文](README.md)

A __MOD_SUMMARY_EN__ mod for Slay the Spire 2, supporting both game branches: 0.107.1 (stable) and 0.111.0 (beta). See [STATUS.md](STATUS.md) for implemented state and limits.

## Installation

This checkout provides source code, bilingual localization, text resource configuration, and organized public design documents. The preferred install path is subscribing on Steam Workshop together with [RitsuLib](https://steamcommunity.com/sharedfiles/filedetails/?id=3747602295) — the workshop item picks the matching content for the running game version, so switching branches needs no reinstall. Alternatively, download the zip for your game target from [GitHub Releases](https://github.com/__REPO__/releases) and place its `__MOD_ID__/` directory under the game's `mods/` directory. Close the game before installing (the game scans `mods/` recursively — keep backups outside it), and keep the previous package for rollback. Minimum dependency versions are defined in the [mod manifest](__MOD_ID__.json). Multimedia is absent from source checkouts; a DLL alone is not a complete installable package.

## Development

Requirements: Bash, Python 3.11+, and the .NET SDK selected by `global.json`. Full asset builds also require the Godot 4.5.1 standard editor and local artwork. Obtain game reference assemblies from your own matching game installation. RitsuLib must include `compat/`, `shared/`, and `RitsuLib.References.props`.

```bash
cp .local-dev.env.example .local-dev.env   # Configure local dependency and tool locations
./scripts/check.sh                 # Source checks; no game DLLs or artwork required
./scripts/restore-refs.sh          # Copy references from GAME_DIR
./scripts/build.sh --dll-only      # Compile the DLL only
./scripts/check.sh --full          # Full assets, compilation, and PCK checks
```

See the [contributor guide](CONTRIBUTING.md) and [build pipeline](docs/dev/pipeline.md). Read the private entry `local_dev/README.md` first when a local workspace exists.

## Documentation

- [Documentation index](docs/README.md) · [Developer docs](docs/dev/README.md) · [Design docs](docs/design/README.md) · [Technical history](docs/history/README.md) · [Changelog](CHANGELOG.md) · [Roadmap](docs/roadmap.md)
- Community: [Code of conduct](CODE_OF_CONDUCT.md), [Security policy](SECURITY.md), [Support](SUPPORT.md), [Credits](CREDITS.md).

## License and artwork

Original software is licensed under [MIT](LICENSE). See the [licensing scope](LICENSING.md) and [third-party notices](THIRD_PARTY_NOTICES.md). Art masters are supplied by this mod's contributors in their own local directory or private repository; asset permissions must be recorded separately. The public source repository stays media-free; Git LFS is not used.

Derived from [STS2-Template](https://github.com/SlayTheCircle/STS2-Template).
