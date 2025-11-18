# Ailin¹ CLI for PyPI

This package (`ailinone-dev-tool`) exposes the official Ailin¹ developer CLI through
PyPI. The CLI itself is written in Node.js and published to npm as
`@ailin/dev-tool`. The PyPI wrapper automates the following steps:

1. Detects a local Node.js + npm toolchain.
2. Downloads `@ailin/dev-tool` (matching this package version) with npm into
   an isolated cache under the current user.
3. Runs the bundled CLI entry point (`dist/cli.bundle.cjs`) with the arguments
   provided to the Python entry point.

This keeps the Python package lightweight while still delivering the full CLI
experience across platforms. Installation always happens inside the current
user profile (no global npm install is required).

## Requirements

- Python 3.9 or newer (needed only for the launcher).
- Node.js 18+ and npm available on the `PATH`.
- Network access to `registry.npmjs.org` the first time the CLI is launched (to
  download the npm package and its dependencies).

## Installation

```bash
pip install ailinone-dev-tool
```

## Usage

Once installed you can invoke the CLI exactly like the npm distribution:

```bash
ailin --help
```

The first execution will bootstrap the npm package. Subsequent runs reuse the
cached installation. To force a reinstall set the environment variable
`AILINONE_CLI_FORCE_INSTALL=1` before invoking the command.

## Troubleshooting

- **`npm` or `node` not found** – Install the latest Node.js LTS build from
  [nodejs.org](https://nodejs.org/) and ensure the installers add the commands
  to your shell `PATH`.
- **Corporate proxies** – Configure `npm` proxy settings globally or set
  `https_proxy`/`http_proxy` before running the CLI to allow `npm install`
  during bootstrapping.
- **Different install location** – Override the cache directory with the
  `AILINONE_CLI_HOME` environment variable.

## License

ISC License – see `LICENSE`.

