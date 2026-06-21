# Release

## Python Wheel

Build locally:

```bash
python3 -m pip wheel . --no-deps --no-build-isolation -w dist
```

Install locally:

```bash
python3 -m pip install dist/sephirot-*.whl
sephirot profile
```

The wheel includes:

- `sephirot` console script
- Python framework package
- core template pack manifest
- core template registry manifest

## VS Code Extension

Package from the extension directory:

```bash
cd integrations/vscode
npm install
npx @vscode/vsce package
code --install-extension sephirot-*.vsix
```

The VS Code extension is a thin shell over the Python CLI.
It should not duplicate graph logic.
