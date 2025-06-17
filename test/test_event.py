# test_events.py
import asyncio
from unittest.mock import Mock, call

import pytest

from nexios import get_application
from nexios.events import (
    EventEmitter,
    EventPhase,
    EventPriority,
)


# Fixture for app with event emitter, ensuring clean state
@pytest.fixture
def app_with_emitter():
    app = get_application()
    app.emitter = EventEmitter()
    yield app
    app.emitter.remove_all_events()


# Fixture for a mock object to track listener calls
@pytest.fixture
def listener_mock():
    return Mock()


# Test basic event registration and triggering
@pytest.mark.asyncio
async def test_app_event_registration_and_trigger(app_with_emitter, listener_mock):
    app = app_with_emitter

    async def startup_handler():
        listener_mock("started")

    # Register listener explicitly
    app.emitter.event("app:startup").listen(startup_handler)

    # Trigger event and ensure completion
    stats = app.emitter.emit("app:startup")

    # Allow async tasks to complete
    await asyncio.sleep(0)  # Yield to event loop

    assert stats["listeners_executed"] == 1
    assert listener_mock.call_args_list == [call("started")]


# Test one-time listeners
@pytest.mark.asyncio
async def test_app_one_time_listener(app_with_emitter, listener_mock):
    app = app_with_emitter

    async def request_handler():
        listener_mock("handled")

    # Register one-time listener
    app.emitter.event("app:request").once(request_handler)

    # Trigger twice
    stats1 = app.emitter.emit("app:request")
    stats2 = app.emitter.emit("app:request")

    # Allow async tasks to complete
    await asyncio.sleep(0)

    assert stats1["listeners_executed"] == 1
    assert stats2["listeners_executed"] == 0  # Listener removed after first trigger
    assert listener_mock.call_args_list == [call("handled")]


# Test event priorities
@pytest.mark.asyncio
async def test_app_event_priorities(app_with_emitter, listener_mock):
    app = app_with_emitter

    async def high_priority():
        listener_mock("high")

    async def low_priority():
        listener_mock("low")

    # Register listeners with different priorities
    app.emitter.event("app:process").listen(high_priority, priority=EventPriority.HIGH)
    app.emitter.event("app:process").listen(low_priority, priority=EventPriority.LOW)

    # Trigger event
    stats = app.emitter.emit("app:process")

    # Allow async tasks to complete
    await asyncio.sleep(0)

    assert stats["listeners_executed"] == 2
    assert listener_mock.call_args_list == [call("high"), call("low")]


# Test event propagation (parent-child)
@pytest.mark.asyncio
async def test_app_event_propagation(app_with_emitter, listener_mock):
    app = app_with_emitter
    parent_event = app.emitter.event("app:parent")
    child_event = app.emitter.event("app:child")
    child_event.parent = parent_event

    async def parent_handler(*args, phase=EventPhase.AT_TARGET):
        listener_mock(f"parent-{phase.name}")

    async def child_handler(*args, phase=EventPhase.AT_TARGET):
        listener_mock(f"child-{phase.name}")

    # Register listeners
    parent_event.listen(parent_handler)
    child_event.listen(child_handler)

    # Trigger child event
    stats = app.emitter.emit("app:child")

    # Allow async tasks to complete
    await asyncio.sleep(0)

    assert stats["listeners_executed"] == 1  # Only child listeners at target phase
