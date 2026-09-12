---
title: Packages
description: Sillo ships as a small core plus separately versioned packages. This is what exists and what each one is for.
---

Sillo's core is one distribution — `sillo-framework` — and everything on this
page installs alongside it. They are separate for one reason each, and the
reason is always the same shape: the package has a dependency, a release
cadence, or a scope that the core should not carry on everybody's behalf.

| Package | Install | Import | What it is |
|---|---|---|---|
| [Wire](/packages/wire/) | `sillo-wire` | `sillo_wire` | Rooms, presence and fan-out for WebSockets |
| [GraphQL](/packages/graphql/) | `sillo-graphql` | `sillo_graphql` | A production GraphQL endpoint over a Strawberry schema |
| [Warder](/packages/warder/) | `warder` | `warder` | A declarative admin over your models |

Each has a manual of its own — pick one above and the sidebar becomes its
table of contents.

## How they attach

Every package is a plain top-level distribution with a plain top-level import
name. Install `sillo-wire`, import `sillo_wire`:

```python
from sillo_wire import Hub, Peer
from sillo_graphql import Graph, field
```

Warder is the exception to the naming rule, and the difference is deliberate.
It is not an extension of `sillo` — it is an application you mount on yours,
the way you would mount any other — so it keeps its own name:

```python
from warder import Admin
admin.mount(app)
```

Nothing is ever written into the framework's own `sillo` package directory.
Shipping `sillo/wire/` in there is simpler, and it is what Wire did first — but
two distributions sharing one directory goes wrong in both directions.
Installing the framework from a checkout moves where `sillo` resolves and
orphans the copy in site-packages; removing or replacing the framework leaves
that directory standing with no `__init__.py` in it, which is an override
rather than an addition. Uninstalling either package leaves the other
untouched.

Wire and GraphQL previously also answered to `sillo.wire` and `sillo.graphql`,
through a meta-path finder registered by a `.pth` at interpreter startup and a
second set of PEP 561 stubs to serve type checkers. It read as part of the
framework, at the cost of a `.pth` running on every interpreter start and type
declarations kept in two places. Those aliases are gone; the `sillo_` names
above are the only ones.

## What stays in core

Anything with no third-party dependency that every application is likely to
reach for. The line is not size — it is whether keeping something in core
forces a decision on people who will never use it.
