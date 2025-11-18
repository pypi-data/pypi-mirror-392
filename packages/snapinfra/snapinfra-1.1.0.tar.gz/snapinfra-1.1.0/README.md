# SnapInfra

[![PyPI version](https://badge.fury.io/py/snapinfra.svg)](https://badge.fury.io/py/snapinfra)
[![Downloads](https://pepy.tech/badge/snapinfra)](https://pepy.tech/project/snapinfra)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**AI-powered infrastructure code generation from natural language**

Transform plain English into production-ready infrastructure code and architecture diagrams. SnapInfra generates Terraform, Kubernetes, Docker configurations with beautiful visualizations using state-of-the-art AI models.

```bash
pip install snapinfra
snapinfra
```

## ✨ What's New in v1.1.0

- **🎨 Architecture-First Workflow**: Automatically generates architecture diagrams before infrastructure code
- **📊 Enhanced Progress Tracking**: Real-time progress bars with ETA and time elapsed
- **🖥️ Syntax-Highlighted Previews**: Beautiful code previews directly in terminal
- **🌳 Interactive File Trees**: Visual tree view of all generated files
- **⚡ Streamlined UX**: Cleaner messaging, better prompts, no clutter
- **🎯 Smart Detection**: Automatically detects infrastructure type and formats output

## Key Features

- **Architecture-First Generation**: Diagrams generated first, then infrastructure code
- **Multi-Format Diagrams**: Python (diagrams library), Mermaid, D2 - all in one command
- **Interactive Terminal**: Progress bars, syntax highlighting, file previews
- **Multi-Provider AI**: OpenAI, Groq, AWS Bedrock, Ollama support
- **Production-Ready**: Security best practices and scalability built-in
- **Browser Viewer**: Optional localhost diagram viewer with zoom and export
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

**Install**
```bash
pip install snapinfra
```

**Set API Key**
```bash
# Free Groq API (recommended)
export GROQ_API_KEY="your-api-key"

# Or OpenAI
export OPENAI_API_KEY="your-api-key"
```

**Generate Infrastructure**
```bash
# AWS Infrastructure
snapinfra "terraform for AWS VPC with public/private subnets"

# Kubernetes
snapinfra "k8s deployment for nginx with ingress"

# Docker
snapinfra "docker-compose for React app with PostgreSQL"

# With specific AI provider
snapinfra -b groq "serverless architecture with API Gateway and Lambda"
```

## Supported Infrastructure

| Platform | Templates | Features |
|----------|-----------|----------|
| **Terraform** | AWS, Azure, GCP | Multi-cloud, modules, best practices |
| **Kubernetes** | Deployments, Services, Ingress | RBAC, security policies, monitoring |
| **Docker** | Dockerfiles, Compose | Multi-stage, optimization, security |
| **CloudFormation** | Serverless, Containers | AWS native, nested stacks |
| **Ansible** | Configuration, Deployment | Automation, orchestration |
| **Helm** | Charts, Values | Kubernetes package management |

## AI Providers

| Provider | Speed | Cost | Best For |
|----------|-------|------|----------|
| **Groq** | Ultra-fast | Free tier | Development, prototyping |
| **OpenAI** | Fast | Pay-per-use | Production, complex scenarios |
| **AWS Bedrock** | Fast | Enterprise | AWS environments |
| **Ollama** | Variable | Free | Privacy, offline usage |

### Setup Examples

**Groq (Recommended)**
```bash
export GROQ_API_KEY="gsk_..."
snapinfra -b groq "terraform for EKS cluster"
```

**OpenAI**
```bash
export OPENAI_API_KEY="sk-..."
snapinfra -b openai -m gpt-4 "complex microservices architecture"
```

**Local with Ollama**
```bash
# No API key needed
snapinfra -b ollama "docker setup for development"
```

## 🎯 Enhanced User Experience

SnapInfra v1.1.0 features a dramatically improved terminal interface:

```bash
snapinfra > create AWS VPC with Terraform

Generating TERRAFORM Infrastructure

Step 1/2: Creating Architecture Diagrams
Generating Python, Mermaid, and D2 formats

⠋ Analyzing infrastructure and creating diagrams... ████████████░░░░  75%  0:00:12  0:00:04

✓ terraform_architecture.py
✓ terraform_architecture.mmd
✓ terraform_architecture.d2

[SUCCESS] Diagrams created successfully (3 files)

Step 2/2: Creating Infrastructure Code
Writing terraform configuration

⠋ Writing infrastructure configuration... ████████████████████  100%  0:00:08  0:00:00

✓ terraform_infrastructure.tf
156 lines

[SUCCESS] All files generated successfully!

TERRAFORM Infrastructure
├── Architecture Diagrams
│   ├── terraform_architecture.py (1.2 KB)
│   ├── terraform_architecture.mmd (856 bytes)
│   └── terraform_architecture.d2 (723 bytes)
└── Infrastructure Code
    └── terraform_infrastructure.tf (4.5 KB)

Show code preview in terminal? [Y/n]
Open architecture viewer in browser? [y/N]
```

**Features:**
- ✅ Real-time progress bars with ETA
- ✅ Clean, professional output
- ✅ Interactive file tree visualization
- ✅ Syntax-highlighted code previews
- ✅ Architecture-first generation workflow

## Common Use Cases

**Cloud Infrastructure**
```bash
# Complete AWS setup
snapinfra "3-tier architecture: ALB, ECS, RDS with monitoring"

# Multi-cloud
snapinfra "hybrid setup: AWS primary, Azure DR"

# Serverless
snapinfra "event-driven architecture with Lambda and SQS"
```

**Container Orchestration**
```bash
# Microservices
snapinfra "k8s platform: ingress, services, deployments, monitoring"

# Development environment
snapinfra "docker-compose: app, database, redis, monitoring"

# Production setup
snapinfra "helm chart for multi-tier application"
```

**Development Workflows**
```bash
# CI/CD
snapinfra "GitHub Actions: test, build, deploy to EKS"

# Infrastructure as Code
snapinfra "Terraform modules for reusable VPC patterns"

# Security
snapinfra "k8s network policies and RBAC for microservices"
```

## Advanced Features

**Interactive Chat Mode**
```bash
snapinfra "basic AWS setup"
# SnapInfra generates initial code
# Continue refining: "add monitoring", "make it multi-region", "add security groups"
```

**Architecture as Code 🆕**
```bash
# Generate diagrams in multiple formats
snapinfra diagram generate "3-tier AWS architecture" --view

# View diagrams interactively
snapinfra diagram view architecture.mmd

# Get example diagrams
snapinfra diagram example
```

See **[QUICKSTART_DIAGRAMS.md](QUICKSTART_DIAGRAMS.md)** for the complete diagram guide.

**Multiple Output Formats**
```bash
# Save to files
snapinfra -o main.tf "terraform VPC setup"
```

**Batch Processing**
```bash
# Multiple environments
snapinfra "terraform modules for dev, staging, prod"

# Different cloud providers
snapinfra "same app architecture for AWS, Azure, GCP"
```

## Configuration

**Environment Variables (Simple)**
```bash
# Choose your AI provider
export GROQ_API_KEY="gsk_..."
export OPENAI_API_KEY="sk_..."
```

**TOML Config (Advanced)**
```toml
# ~/.config/snapinfra/config.toml
default_backend = "groq"

[backends.groq]
type = "groq"
api_key = "$GROQ_API_KEY"
default_model = "llama-4-scout-17b"

[backends.openai]
type = "openai"
api_key = "$OPENAI_API_KEY"
default_model = "gpt-4"

[backends.bedrock]
type = "bedrock"
aws_profile = "default"
aws_region = "us-east-1"
```

## CLI Reference

**Basic Usage**
```bash
snapinfra [OPTIONS] "your infrastructure description"
```

**Common Options**
```bash
-b, --backend TEXT     AI provider (groq, openai, bedrock, ollama)
-m, --model TEXT       Specific model to use
-o, --output FILE               Save code to file
-q, --quiet                      Non-interactive mode
--list-models                    Show available models
--validate / --no-validate       Run validation after generation (default from config)
--save-validation-report         Save validation report to the project directory
--report-format [markdown|json|text]  Format for saved validation report
```

**Examples**
```bash
snapinfra -b groq "k8s setup"
snapinfra -o main.tf "terraform VPC"
snapinfra --clipboard "docker compose"
```

## Why Choose SnapInfra?

**For Developers**
- Generate infrastructure faster than manual coding
- Learn best practices through AI-generated examples
- Consistent, documented infrastructure code
- Works with your existing tools and workflows

**For Teams**
- Standardize infrastructure patterns across projects
- Reduce knowledge silos with documented code
- Faster onboarding with readable, explained infrastructure
- Multi-environment consistency (dev/staging/prod)

**For Enterprises**
- Security best practices built into every template
- Compliance-ready configurations
- Cost-optimized resource specifications
- Integration with existing CI/CD pipelines

## Enterprise Support

**Professional Services**
- Custom AI model integration
- Enterprise template development
- Team training and onboarding
- Architecture review and optimization

**Support Channels**
- GitHub Issues: Bug reports and feature requests
- Enterprise Support: Priority support and SLA
- Community: Discussions and examples

**Compliance & Security**
- SOC 2 compliant infrastructure templates
- CIS benchmarks integration
- Security scanning and validation
- Audit logging and compliance reporting

## Development

**From Source**
```bash
git clone https://github.com/manojmaheshwarjg/snapinfra-cli.git
cd snapinfra-cli
pip install -e ".[dev]"
```

**Testing**
```bash
pytest
pytest --cov=snapinfra
```

**Contributing**
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

**Project Structure**
```
src/snapinfra/
├── cli/          # Command-line interface
├── backends/     # AI provider implementations  
├── config/       # Configuration management
├── types/        # Data models and types
└── utils/        # Utility functions
```

## License

**Apache License 2.0**

SnapInfra is open-source software licensed under the Apache License 2.0. This means:

- Commercial use allowed
- Modification and distribution permitted  
- Patent protection provided
- Private use permitted
- Must include license and copyright notice
- Must state changes made to the code

---

**Built by developers, for developers**

[GitHub](https://github.com/manojmaheshwarjg/snapinfra-cli) • [PyPI](https://pypi.org/project/snapinfra/) • [Issues](https://github.com/manojmaheshwarjg/snapinfra-cli/issues) • [Discussions](https://github.com/manojmaheshwarjg/snapinfra-cli/discussions)

