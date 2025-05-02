---
icon: speed
---

# Performance

Let's talk honestly about Nexios's performance. We believe in transparency over marketing.

## Current State

### How We Compare

As a newer framework, we're still optimizing our performance. Here's where we stand:

- **vs FastAPI**: FastAPI is currently faster—it's highly optimized and mature. We're working to close the gap, but we prioritize developer experience alongside performance.
  
- **vs Django**: We generally perform better in basic request handling, though Django has advantages in certain areas due to its maturity.
  
- **vs Flask**: Similar performance characteristics, with some operations being faster in Nexios due to our modern architecture.

### Benchmark Context

Important notes about our benchmarks:

1. We're early in our journey—many optimizations are still coming
2. We focus on real-world usage patterns, not just synthetic benchmarks
3. We're committed to improving while maintaining simplicity

## Performance Goals

Our target areas for optimization:

1. Request routing speed
2. Middleware execution efficiency
3. Memory usage in high-load scenarios
4. Response generation time

## When to Choose Nexios

Choose Nexios when:

- You value developer experience alongside performance
- Your project needs good-enough performance with great flexibility
- You're building something that might need to scale later

Consider alternatives when:

- Absolute maximum performance is your top priority (consider FastAPI)
- You need proven production performance at massive scale (consider Django)

