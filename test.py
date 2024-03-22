# test_integration.py

from Telemetry.RabbitMQ import TelemetryRabbitMQ

def test_telemetry_rabbitmq():
    # Initialize TelemetryRabbitMQ instance
    rabbitmq = TelemetryRabbitMQ("eru","hostname")

    # Test sending a message
    message = "Test message"
    result = rabbitmq.send_message(message)

    # Check if message was sent successfully
    assert result == True, "Failed to send message"

    # Test receiving a message
    received_message = rabbitmq.receive_message()

    # Check if received message matches the sent message
    assert received_message == message, "Received message does not match sent message"

    print("Integration library tests passed successfully!")

if __name__ == "__main__":
    test_telemetry_rabbitmq()
