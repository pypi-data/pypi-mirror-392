# Memory Profiling Documentation

This directory contains comprehensive documentation for memory profiling and optimization in the Competency API.

## Documentation Overview

### 📋 [Memory Profiling Guide](MEMORY_PROFILING_GUIDE.md)
**The complete reference** for memory profiling in the Competency API.

- **What it covers**: All profiling tools, optimization strategies, and workflows
- **Who it's for**: Developers doing optimization work and performance analysis
- **Length**: Comprehensive (50+ pages)
- **Use when**: You need detailed information about any aspect of memory profiling

### 🚀 [Setup Guide](SETUP_GUIDE.md)  
**Step-by-step setup instructions** for memory profiling tools.

- **What it covers**: Installation, configuration, and verification of profiling setup
- **Who it's for**: New developers setting up the profiling environment
- **Length**: Detailed setup instructions
- **Use when**: First time setting up memory profiling or troubleshooting setup issues

### 💡 [Usage Examples](USAGE_EXAMPLES.md)
**Practical examples** showing how to use memory profiling tools.

- **What it covers**: 15+ real-world examples from basic to advanced usage
- **Who it's for**: Developers wanting to see concrete usage patterns
- **Length**: Example-focused with code snippets
- **Use when**: You want to see how to apply profiling tools to specific scenarios

### 🔧 [Troubleshooting](TROUBLESHOOTING.md)
**Solutions to common issues** encountered during memory profiling.

- **What it covers**: Setup problems, runtime issues, platform-specific problems
- **Who it's for**: Developers encountering problems with profiling tools
- **Length**: Problem/solution focused
- **Use when**: Something isn't working and you need a fix

### 📈 [Optimization Workflow](OPTIMIZATION_WORKFLOW.md)
**Systematic process** for identifying and implementing memory optimizations.

- **What it covers**: 6-phase optimization process from baseline to monitoring
- **Who it's for**: Developers planning optimization work
- **Length**: Process-focused with templates and checklists
- **Use when**: Starting an optimization project or need a structured approach

## Quick Navigation

### I want to...

#### Get started with memory profiling
→ Start with [Setup Guide](SETUP_GUIDE.md), then [Usage Examples](USAGE_EXAMPLES.md)

#### Understand all profiling capabilities  
→ Read the [Memory Profiling Guide](MEMORY_PROFILING_GUIDE.md)

#### Fix a specific problem
→ Check [Troubleshooting](TROUBLESHOOTING.md)

#### Optimize memory usage systematically
→ Follow the [Optimization Workflow](OPTIMIZATION_WORKFLOW.md)

#### See how to profile specific components
→ Look at [Usage Examples](USAGE_EXAMPLES.md) sections 2-3

#### Set up CI/CD monitoring
→ See [Optimization Workflow](OPTIMIZATION_WORKFLOW.md) section 9

## Quick Reference Commands

```bash
# Basic profiling test
cargo test --features memory-profiling profiling -- --nocapture

# Get baseline measurements
cargo test --features memory-profiling test_baseline_memory_usage -- --nocapture

# Generate detailed DHAT analysis
cargo run --example memory_profile --features memory-profiling

# Run memory benchmarks
cargo bench --features memory-profiling

# View DHAT report
dh_view.py dhat-heap.json
```

## Document Structure

Each document follows a consistent structure:

- **Table of Contents** - Easy navigation to specific topics
- **Overview** - Quick summary of what's covered
- **Detailed Sections** - Step-by-step instructions or examples
- **Commands/Code** - Ready-to-use snippets
- **Troubleshooting** - Common issues within that topic
- **Next Steps** - Where to go after completing the document

## Prerequisites

Before using these guides, ensure you have:

- Rust 1.70+
- Python 3.7+ (for DHAT viewer)
- Basic familiarity with Cargo and Rust development
- Understanding of memory allocation concepts (helpful but not required)

## Getting Help

If you can't find what you're looking for:

1. **Check the troubleshooting sections** in each document
2. **Use the search functionality** in your editor/browser
3. **Look at the examples** - they often show solutions to common tasks
4. **Check the main README** for basic usage patterns

## Contributing to Documentation

When updating these docs:

- **Keep examples up-to-date** with the current API
- **Test all commands** on a clean environment
- **Update cross-references** when adding new sections
- **Maintain consistent formatting** across documents
- **Include output examples** for commands where helpful

## Documentation Maintenance

| Document | Last Updated | Next Review |
|----------|--------------|-------------|
| Memory Profiling Guide | Current | As needed |
| Setup Guide | Current | With major dependency updates |
| Usage Examples | Current | When API changes |
| Troubleshooting | Current | When new issues arise |
| Optimization Workflow | Current | Quarterly review |

---

**📝 Remember**: These docs are living documents. As the codebase evolves and new optimization techniques are discovered, keep the documentation updated to maintain its usefulness.