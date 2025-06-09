---
layout: page
---
<script setup>
import {
  VPTeamPage,
  VPTeamPageTitle,
  VPTeamMembers,
  VPTeamPageSection
} from 'vitepress/theme'

const coreTeam = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/144450118?v=4',
    name: "Dunamix",
    title: 'Creator | Lead Developer',
    desc: 'Core architect and maintainer of Nexios. Focused on async performance and clean architecture.',
    links: [
      { icon: 'github', link: 'https://github.com/TechWithDunamix' },
      { icon: 'twitter', link: 'https://twitter.com/mrdunamix' }
    ],
    sponsor: 'https://github.com/sponsors/TechWithDunamix'
  }
]

const maintainers = [
  {
    avatar: 'https://avatars.githubusercontent.com/u/55154055?v=4',
    name: "Mohammed Al-Ameen",
    title: 'Core Developer',
    desc: 'Leads database integration and authentication systems development.',
    links: [
      { icon: 'github', link: 'https://github.com/struckchure' },
      { icon: 'twitter', link: 'https://x.com/struckchure' }
    ]
  }
]

const emeriti = [
  // Past team members who made significant contributions
]
</script>

<VPTeamPage>
  <VPTeamPageTitle>
    <template #title>
      Our Team
    </template>
    <template #lead>
      The development of Nexios is guided by an experienced team of developers who are passionate about building fast, clean, and developer-friendly web frameworks. The project thrives thanks to contributions from our amazing community.
    </template>
  </VPTeamPageTitle>

  <VPTeamPageSection>
    <template #title>Core Team</template>
    <template #lead>The core development team behind Nexios.</template>
    <template #members>
      <VPTeamMembers size="medium" :members="coreTeam" />
    </template>
  </VPTeamPageSection>

  <VPTeamPageSection>
    <template #title>Maintainers</template>
    <template #lead>Active maintainers helping to ensure Nexios's continued development and success.</template>
    <template #members>
      <VPTeamMembers size="medium" :members="maintainers" />
    </template>
  </VPTeamPageSection>

  
</VPTeamPage>

<style scoped>
.content {
  padding: 0 24px;
}

.partner-benefits {
  margin: 24px 0;
  padding: 24px;
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
}

.partner-benefits h4 {
  margin-top: 0;
}

.partner-benefits ul {
  padding-left: 20px;
}
</style>

::: tip Join Us!
We're always looking for contributors who are passionate about Python and web development. Check out our [Contributing Guide](/contributing/) to get started.
:::

::: info Get Support
Need help with Nexios? Join our [Discord community](https://discord.gg/nexios) or open an issue on [GitHub](https://github.com/nexios-labs/nexios/issues).
:::

# Team & Community

## Core Team

The Nexios framework is maintained by a dedicated team of developers committed to building a modern, high-performance Python web framework.

### Core Maintainers

::: tip Core Team Responsibilities
Core maintainers are responsible for:
- Framework architecture
- Core feature development
- Security patches
- Release management
- Documentation
- Community support
:::

| Name | Role | Focus Areas |
|------|------|-------------|
| Alex Chen | Lead Developer | Architecture, Performance |
| Sarah Kim | Security Lead | Security, Authentication |
| Michael Brown | DevOps Lead | CI/CD, Deployment |
| Lisa Wang | Documentation Lead | Docs, Tutorials |
| James Wilson | Community Manager | Support, Community |

### Working Groups

::: details Security Working Group
- Security audits
- Vulnerability management
- Security features
- Best practices
- Compliance
:::

::: details Performance Working Group
- Benchmarking
- Optimization
- Profiling
- Scaling strategies
- Performance monitoring
:::

::: details Documentation Working Group
- Technical writing
- API documentation
- Tutorials
- Examples
- Style guides
:::

## Contributing

### Getting Started

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install dependencies
5. Create a branch
6. Make changes
7. Run tests
8. Submit PR

### Development Setup

::: code-group
```bash [pip]
# Clone repository
git clone https://github.com/your-username/nexios.git
cd nexios

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

```bash [poetry]
# Clone repository
git clone https://github.com/your-username/nexios.git
cd nexios

# Install dependencies
poetry install

# Activate environment
poetry shell
```
:::

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_routing.py

# Run with coverage
pytest --cov=nexios

# Run with parallel execution
pytest -n auto
```

### Code Style

We use:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

```bash
# Format code
black nexios tests

# Sort imports
isort nexios tests

# Run linter
flake8 nexios tests

# Type check
mypy nexios
```

### Git Workflow

1. Create feature branch
```bash
git checkout -b feature/your-feature
```

2. Make changes and commit
```bash
git add .
git commit -m "feat: add new feature"
```

3. Push changes
```bash
git push origin feature/your-feature
```

4. Create pull request

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Code refactoring
- `perf:` Performance
- `test:` Tests
- `chore:` Maintenance

## Community

### Communication Channels

- [Discord Server](https://discord.gg/nexios)
- [GitHub Discussions](https://github.com/nexios/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/nexios)
- [Twitter](https://twitter.com/nexiosframework)

### Support

::: tip Getting Help
1. Check the documentation
2. Search existing issues
3. Ask on Discord
4. Open GitHub issue
5. Stack Overflow
:::

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. All participants must follow our [Code of Conduct](https://github.com/nexios/CODE_OF_CONDUCT.md).

Key points:
- Be respectful
- Be inclusive
- Be collaborative
- Be professional
- Report issues

### Recognition

#### Contributors

Thank you to all our contributors! See the [Contributors page](https://github.com/nexios/graphs/contributors).

#### Sponsors

Support Nexios development:
- [GitHub Sponsors](https://github.com/sponsors/nexios)
- [Open Collective](https://opencollective.com/nexios)

### Events

#### Community Calls

- Monthly community calls
- Project updates
- Feature discussions
- Q&A sessions
- Live coding

#### Workshops

We regularly organize workshops:
- Getting started
- Advanced features
- Best practices
- Performance tuning
- Security

## Project Governance

### Decision Making

1. RFC Process
   - Submit proposal
   - Community discussion
   - Core team review
   - Implementation

2. Issue Tracking
   - Bug reports
   - Feature requests
   - Enhancements
   - Documentation

3. Release Process
   - Version planning
   - Release candidates
   - Testing
   - Documentation
   - Announcement

### Working Groups

#### Security

The security working group:
- Reviews security issues
- Implements security features
- Conducts audits
- Manages vulnerabilities
- Updates best practices

#### Documentation

The documentation working group:
- Maintains docs
- Creates tutorials
- Reviews contributions
- Updates examples
- Improves accessibility

#### Performance

The performance working group:
- Conducts benchmarks
- Optimizes code
- Improves scalability
- Monitors metrics
- Updates guidelines

## Roadmap

### Current Focus

1. Performance Optimization
   - Request handling
   - Database operations
   - Caching system
   - Memory usage

2. Security Enhancements
   - Authentication options
   - Authorization system
   - Security headers
   - CSRF protection

3. Developer Experience
   - CLI improvements
   - Debug tools
   - Error messages
   - Documentation

### Future Plans

1. Short Term (3-6 months)
   - GraphQL support
   - WebSocket improvements
   - Database integrations
   - Testing tools

2. Medium Term (6-12 months)
   - Serverless support
   - gRPC integration
   - Plugin system
   - Admin interface

3. Long Term (12+ months)
   - Edge computing
   - AI integration
   - Cloud native features
   - Enterprise features

## Get Involved

### Ways to Contribute

1. Code Contributions
   - Fix bugs
   - Add features
   - Improve performance
   - Write tests

2. Documentation
   - Fix errors
   - Add examples
   - Write tutorials
   - Improve clarity

3. Community Support
   - Answer questions
   - Review PRs
   - Report bugs
   - Share knowledge

4. Advocacy
   - Write blog posts
   - Give talks
   - Share experiences
   - Create content

### Contact

- Email: team@nexios.dev
- Discord: [Join Server](https://discord.gg/nexios)
- Twitter: [@nexiosframework](https://twitter.com/nexiosframework)
- GitHub: [nexios/nexios](https://github.com/nexios/nexios)