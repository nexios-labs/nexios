---
layout: home
title: 28 Days of Nexios
hero:
  name: "28 Days of Nexios"
  text: "Master Web Development with Nexios Framework"
  tagline: A comprehensive journey from basics to production-ready applications
  image:
    src: /icon.svg
    alt: Nexios Logo
  actions:
    - theme: brand
      text: Get Started
      link: /course/day01/
    - theme: alt
      text: View on GitHub
      link: https://github.com/nexios-labs/nexios
features:
  - icon: 🚀
    title: Fundamentals First
    details: Start with the basics and progressively build your knowledge of web development with Nexios.
  - icon: 🔒
    title: Security & Auth
    details: Learn best practices for authentication, authorization, and securing your applications.
  - icon: ⚡
    title: Real-time Apps
    details: Build modern real-time applications with WebSockets and advanced features.
  - icon: 🛠
    title: Production Ready
    details: Master deployment, testing, and optimization for production environments.
---

# Course Overview

<div class="course-grid">
  <div v-for="day in days" :key="day.name" class="course-card">
    <h3>{{ day.name }}</h3>
    <p>{{ day.title }}</p>
    <a :href="day.link" class="start-button">Start</a>
  </div>
</div>

<script setup>
const days = [
  {
    name: 'Day 1',
    title: 'Welcome & Your First Nexios App',
    link: '/course/day01/'
  },
  {
    name: 'Day 2',
    title: 'Routing: Mapping URLs to Code',
    link: '/course/day02/'
  },
  {
    name: 'Day 3',
    title: 'Async, Request & Response Essentials',
    link: '/course/day03/'
  },
  {
    name: 'Day 4',
    title: 'Class-Based Views & APIHandler',
    link: '/course/day04/'
  },
  {
    name: 'Day 5',
    title: 'Middleware: Built-in & Custom',
    link: '/course/day05/'
  },
  {
    name: 'Day 6',
    title: 'Environment & CORS Configuration',
    link: '/course/day06/'
  },
  {
    name: 'Day 7',
    title: 'Project: Mini To-Do API',
    link: '/course/day07/'
  },
  {
    name: 'Day 8',
    title: 'JWT Authentication (Part 1)',
    link: '/course/day08/'
  },
  {
    name: 'Day 9',
    title: 'JWT Authentication (Part 2)',
    link: '/course/day09/'
  },
  {
    name: 'Day 10',
    title: 'Testing Nexios Applications',
    link: '/course/day10/'
  },
  {
    name: 'Day 11',
    title: 'Request Validation with Pydantic',
    link: '/course/day11/'
  },
  {
    name: 'Day 12',
    title: 'File Uploads & Multipart Data',
    link: '/course/day12/'
  },
  {
    name: 'Day 13',
    title: 'WebSocket Basics',
    link: '/course/day13/'
  },
  {
    name: 'Day 14',
    title: 'Real-Time Chat App with ChannelBox',
    link: '/course/day14/'
  },
  {
    name: 'Day 15',
    title: 'Background Tasks & Scheduling',
    link: '/course/day15/'
  },
  {
    name: 'Day 16',
    title: 'Real-Time Application Patterns',
    link: '/course/day16/'
  },
  {
    name: 'Day 17',
    title: 'Advanced Middleware Techniques',
    link: '/course/day17/'
  },
  {
    name: 'Day 18',
    title: 'Custom Decorators & Utilities',
    link: '/course/day18/'
  },
  {
    name: 'Day 19',
    title: 'Dependency Injection in Nexios',
    link: '/course/day19/'
  },
  {
    name: 'Day 20',
    title: 'Concurrency & Async Utilities',
    link: '/course/day20/'
  },
  {
    name: 'Day 21',
    title: 'Project: Real-Time Chat Application',
    link: '/course/day21/'
  },
  {
    name: 'Day 22',
    title: 'Testing Strategies & Best Practices',
    link: '/course/day22/'
  },
  {
    name: 'Day 23',
    title: 'Logging & Monitoring',
    link: '/course/day23/'
  },
  {
    name: 'Day 24',
    title: 'Performance Optimization',
    link: '/course/day24/'
  },
  {
    name: 'Day 25',
    title: 'Event System & WebSocket Events',
    link: '/course/day25/'
  },
  {
    name: 'Day 26',
    title: 'Deployment Strategies',
    link: '/course/day26/'
  },
  {
    name: 'Day 27',
    title: 'Docker & Containerization',
    link: '/course/day27/'
  },
  {
    name: 'Day 28',
    title: 'Project: Production-Ready API',
    link: '/course/day28/'
  }
]
</script>

<style>
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.course-card {
  background-color: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--vp-c-brand);
}

.course-card h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--vp-c-brand);
}

.course-card p {
  margin: 0.5rem 0 1rem;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  line-height: 1.4;
}

.start-button {
  display: inline-block;
  /* background-color: var(--vp-c-brand); */
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.start-button:hover {
  background-color: var(--vp-c-brand-dark);
  text-decoration: none;
}

/* Support section styling */
.support-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.support-card {
  background-color: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.support-card h3 {
  margin: 0 0 0.5rem;
  color: var(--vp-c-brand);
}

.support-card p {
  margin: 0 0 1rem;
  color: var(--vp-c-text-2);
}
</style>

## Prerequisites

::: info Prerequisites
- Basic Python knowledge
- Understanding of web concepts
- Familiarity with async programming
- Basic command line usage
:::

## Installation Guide

::: code-group
```bash [Linux/Mac]
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Nexios
pip install nexios
```

```bash [Windows]
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install Nexios
pip install nexios
```
:::

## Support & Community

<div class="support-grid">
  <div class="support-card">
    <h3>Discord Community</h3>
    <p>Join our active Discord community</p>
    <a href="https://discord.gg/x3Jm6jsw" class="start-button">Join</a>
  </div>
  <div class="support-card">
    <h3>Stack Overflow</h3>
    <p>Get help from the community</p>
    <a href="https://stackoverflow.com/questions/tagged/nexios" class="start-button">Ask</a>
  </div>
  <div class="support-card">
    <h3>GitHub Issues</h3>
    <p>Report bugs and request features</p>
    <a href="https://github.com/nexios-labs/nexios/issues" class="start-button">Report</a>
  </div>
</div>