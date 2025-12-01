import panties
import time


def test_exception_capture():
    """Test capturing an exception with the global exception hook."""
    print("Test 1: Testing global exception capture...")
    raise ValueError("This is a test exception from global hook")


def test_manual_exception():
    """Test manually capturing an exception."""
    print("\nTest 2: Testing manual exception capture...")
    try:
        x = 1 / 0
    except Exception:
        panties.capture_exception(
            extra={"context": "division by zero test"},
            tags={"test_type": "manual", "severity": "high"}
        )
        print("Exception captured manually!")


def test_message_capture():
    """Test capturing custom messages."""
    print("\nTest 3: Testing message capture...")
    panties.capture_message(
        "This is an info message",
        level="info",
        tags={"test": "message_capture"}
    )
    print("Info message sent!")

    panties.capture_message(
        "This is a warning message",
        level="warning",
        extra={"user_id": 123, "action": "test_action"}
    )
    print("Warning message sent!")


def test_decorator():
    """Test the capture_exceptions decorator."""
    print("\nTest 4: Testing decorator...")

    @panties.capture_exceptions
    def risky_function():
        print("Inside decorated function...")
        raise RuntimeError("Error from decorated function")

    try:
        risky_function()
    except RuntimeError as e:
        print(f"Caught: {e}")


def test_context_manager():
    """Test the capture_exceptions_ctx context manager."""
    print("\nTest 5: Testing context manager...")

    with panties.capture_exceptions_ctx():
        print("Inside context manager...")
        data = {"key": "value"}
        result = data["missing_key"]  # This will raise KeyError


def main():
    print("=== Panties Client Test Suite ===\n")
    print("Initializing panties client...")

    # Initialize the client
    panties.init(
        api_token="d67326dba59fb6e0c26fab57210d73f14be34ded7a4ffe68f1ecb2f21d3b892d",
        endpoint="http://localhost:8000/api/events/",
        environment="dev",
        service_name="my-service-test",
    )
    print("Client initialized!\n")

    # Run tests in order
    try:
        test_manual_exception()
    except Exception as e:
        print(f"Unexpected error in test_manual_exception: {e}")

    try:
        test_message_capture()
    except Exception as e:
        print(f"Unexpected error in test_message_capture: {e}")

    try:
        test_decorator()
    except Exception as e:
        print(f"Unexpected error in test_decorator: {e}")

    try:
        test_context_manager()
    except Exception as e:
        print(f"Expected error from context manager test: {e}")

    print("\n=== All tests completed ===")

    # Give the background thread time to send all events
    print("\nWaiting for events to be sent...")
    time.sleep(1)

    print("\nNow testing global exception hook (this will crash the program)...")

    # This will trigger the global exception hook
    test_exception_capture()


if __name__ == "__main__":
    main()
