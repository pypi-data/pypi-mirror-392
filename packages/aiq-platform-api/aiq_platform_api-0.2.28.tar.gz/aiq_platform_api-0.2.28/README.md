# AttackIQ Platform CLI

⚠️ **BETA / WORK IN PROGRESS** ⚠️

A command-line interface for interacting with the AttackIQ Platform API.

## Status

This project is currently in beta and under active development. Features and APIs may change without notice. Feedback and contributions are welcome!

## Installation

### Build from source

```bash
go build -o aiq ./cmd/aiq
```

### Install globally

```bash
go install ./cmd/aiq
```

## Prerequisites
- Go 1.22+
- Valid AttackIQ Platform credentials
- Basic familiarity with API concepts

## Configuration

Set the following environment variables:

```bash
export ATTACKIQ_PLATFORM_URL="https://your-platform-url.attackiq.com"
export ATTACKIQ_PLATFORM_API_TOKEN="your-api-token"
```

Or create a `.env` file in your working directory:

```env
ATTACKIQ_PLATFORM_URL=https://your-platform-url.attackiq.com
ATTACKIQ_PLATFORM_API_TOKEN=your-api-token
```

## Usage

```bash
# List available commands
aiq --help

# List assessments
aiq assessments list

# Search assets
aiq assets search --query "hostname"

# Get scenario details
aiq scenarios get --scenario-id "abc123"
```

## Shell Completion

The CLI supports shell completion for bash, zsh, fish, and PowerShell.

### Bash

**Current session:**
```bash
source <(aiq completion bash)
```

**Permanent installation:**
```bash
# Linux
aiq completion bash | sudo tee /etc/bash_completion.d/aiq

# macOS
aiq completion bash > $(brew --prefix)/etc/bash_completion.d/aiq
```

### Zsh

**Current session:**
```bash
source <(aiq completion zsh)
```

**Permanent installation:**
```bash
# Add to ~/.zshrc
echo "source <(aiq completion zsh)" >> ~/.zshrc

# Or install to completions directory
aiq completion zsh > "${fpath[1]}/_aiq"
```

### Fish

**Permanent installation:**
```bash
aiq completion fish | source

# Or save to completions directory
aiq completion fish > ~/.config/fish/completions/aiq.fish
```

### PowerShell

**Current session:**
```powershell
aiq completion powershell | Out-String | Invoke-Expression
```

**Permanent installation:**
Add the following to your PowerShell profile:
```powershell
aiq completion powershell | Out-String | Invoke-Expression
```

## Contributing

We welcome feedback and contributions! For detailed contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

Quick ways to contribute:
- Open issues for bugs or feature requests
- Submit pull requests
- Provide feedback on the API design

## License

MIT License - See LICENSE file for details