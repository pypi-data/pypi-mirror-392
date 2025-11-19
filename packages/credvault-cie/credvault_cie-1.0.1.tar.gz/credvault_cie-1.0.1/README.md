# ![Logo](credvault.svg)

Welcome to CredVault - Database-as-a-Service Platform!

## 📚 Documentation

**All documentation has been organized in the [`docs/`](./docs/) directory.**

### Quick Links:
- 🚀 [Quick Start Guide](./docs/getting-started/QUICK_START.md) - Get started in minutes
- 📖 [User Experience Guide](./docs/guides/USER_EXPERIENCE_GUIDE.md) - Learn how to use CredVault
- 🔧 [Advanced API Features](./docs/api/ADVANCED_API_FEATURES.md) - Smart queries, webhooks, batch operations
- 💻 [Backend Development](./docs/development/BACKEND_README.md) - Backend setup
- 🎨 [Frontend Development](./docs/development/FRONTEND_README.md) - Frontend setup

**[Browse All Documentation →](./docs/)**

## Components

- `backend/` - Node.js/Express API server with MongoDB
- `frontend/` - React dashboard application
- `docs/` - Complete project documentation

## Download CredVault

- See our releases page for the latest version
- Using docker image `docker pull credvault/server`

## Download the CredVault Shell

- See our releases page for the latest shell version
- Using package manager: `brew install credvault-shell`

## Building

See [Building CredVault](docs/building.md).

## Running

For command line options invoke:

```bash
$ ./credvaultd --help
```

To run a single server database:

```bash
$ sudo mkdir -p /data/db
$ ./credvaultd
$
$ # The credvault shell connects to localhost and test database by default:
$ ./credvaultsh
test> help
```

## Installing CredVault Studio

You can install CredVault Studio using the `install_studio` script:

```bash
$ ./install_studio
```

This will download the appropriate CredVault Studio package for your platform
and install it.

## Drivers

Client drivers for most programming languages are available in our documentation.

## Bug Reports

Please submit bug reports through our issue tracker.

## Packaging

Packages are created dynamically by the [buildscripts/packager.py](buildscripts/packager.py) script.
This will generate RPM and Debian packages.

## Learn CredVault

- Documentation - See our official documentation
- Developer Center - Visit our developer portal
- CredVault Academy - Start learning at our educational platform

## Cloud Hosted CredVault

Visit our cloud platform page for managed database solutions.

## Community

Join our community forums for:

- Technical questions about using CredVault
- Development discussions and contributions

## LICENSE

CredVault is proprietary software. © 2025 T756-Tech. All rights reserved.

This software and its documentation are protected by copyright law and international treaties. Unauthorized reproduction or distribution of this software, or any portion of it, may result in severe civil and criminal penalties, and will be prosecuted to the maximum extent possible under law.

