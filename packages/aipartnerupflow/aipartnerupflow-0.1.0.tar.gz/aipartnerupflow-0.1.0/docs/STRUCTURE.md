# Documentation Structure

## Organization

Documentation is organized into the following categories:

```
docs/
├── README.md                    # Documentation index
├── STRUCTURE.md                 # This file - documentation structure overview
├── architecture/                # Architecture and design documents
│   ├── ARCHITECTURE.md          # System architecture and design principles
│   ├── DIRECTORY_STRUCTURE.md   # Directory structure and naming conventions
│   ├── NAMING_CONVENTION.md     # Naming conventions for extensions
│   └── EXTENSION_REGISTRY_DESIGN.md  # Extension registry design (Protocol-based)
├── configuration/              # Configuration documentation
│   └── TABLE_CONFIGURATION.md  # Database table configuration
├── development/                 # Development guides
│   ├── DEVELOPMENT.md          # Development guide for contributors
│   ├── CLI_DESIGN.md           # CLI design and implementation
│   └── AGGREGATE_RESULTS_DESIGN.md  # Aggregate results executor design
├── planning/                    # Planning and reference documents
│   ├── CLI_DESIGN.md           # CLI design planning
│   └── IMPLEMENTATION_PLAN.md  # Architecture implementation plan (design phase tasks)
└── usage/                       # Usage guides
    └── CLI_USAGE.md            # CLI usage documentation
```

## Root Directory Files

These files remain in the root directory for visibility:

- **README.md** - Main user guide and quick start (must be in root for GitHub/PyPI)
- **CHANGELOG.md** - Version history and changes (standard location)
- **LICENSE** - License file (standard location)

## Documentation Categories

### Architecture Documents (`docs/architecture/`)
Detailed technical documentation about system design, architecture decisions, and design patterns.

### Development Documents (`docs/development/`)
Guides for developers contributing to the project, including design documents for specific features.

### Configuration Documents (`docs/configuration/`)
Documentation about configuration options and database table settings.

### Planning Documents (`docs/planning/`)
Planning documents and implementation plans. Currently contains the implementation plan for aligning code with the designed architecture.

### Usage Documents (`docs/usage/`)
User guides and usage documentation for end users.

