# GEO Knowledge Hub CLI

`gkh` is the command line entry point for the GEO Knowledge Hub ecosystem.

## Install

```bash
uv tool install gkh-cli
```

Now, you are ready to start exploring!

## Usage

Once you complete the installation, the command `gkh` will be available in your terminal:

```console
$ gkh --version
gkh-cli 0.1.0
```

`gkh` is an entry point, so by default it has no operation commands. To add commands, you need to install plugins. For example, to use the deploy operations, you can install [gkh-deploy](https://github.com/geo-knowledge-hub/gkh-deploy):

```bash
uv tool install --with gkh-deploy gkh-cli
```

You can check which plugins are installed using the `plugins` command:

```console
$ gkh plugins
deploy	gkh-deploy 0.1.0	gkh_deploy.cli:app
```

Now you can use the available operations!

### Configuration

In the base `gkh` command, there are a few options you can use to define which GEO Knowledge Hub instance your commands will act on:

| Option | Environment variable | Meaning |
|---|---|---|
| `--url` | `GKH_BASE_URL` | Base URL of the instance |
| `--token` | `GKH_API_TOKEN` | Personal access token |
| `--no-verify-tls` | `GKH_NO_VERIFY_TLS` | Skip TLS verification |
| `--output text\|json` | — | How groups present results |

You can configure them using a flag (e.g., `--url`) or an environment variable (e.g., `GKH_BASE_URL`). When both are set, the flag is more specific and overrides the environment variable.

## Development

```bash
uv sync
uv run pytest                                        # tests
uv run ruff check . && uv run ruff format --check .  # lint and format
```

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes, and ensure tests, linting and type checks pass before submitting a pull request.

## License

`gkh-cli` is distributed under the MIT license. See [LICENSE](./LICENSE) for the full text.
