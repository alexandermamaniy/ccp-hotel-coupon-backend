"""
aws_services.py

A Python custom library for interacting with Amazon SQS (Simple Queue Service) and SNS (Simple Notification Service) for the app hotel coupon

Author: Alexander Mamani Yucra
Version: 1.0.0
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
import json
import time

class SNSPublishMessageError(Exception):
    """Exception raised for publishing SNS message error.

    Attributes:
        message -- explanation of the SNS publication message error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SNSService:
    """
    SNSService class allows to interact with Amazon SNS (Simple Notification Service) for the hotel coupon app.
    """

    def __init__(self, aws_access_key, aws_secret_key, region_name='us-east-1'):
        """
        Initialize the SNS client with the provided credentials and region.

        :param aws_access_key: The AWS access key ID.
        :param aws_secret_key: The AWS secret access key.
        :param region_name: The AWS region name.
        """
        self.sns_client = boto3.client(
            'sns',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )

    def publish_message(self, target_arn, message, subject=None):
        """
        Publish a message to an SNS topic.

        :param target_arn: The ARN of the target SNS topic.
        :param message: The message to publish. It follows this JSON format. { "user_profile_id": string, "coupon_code": string }
        """
        try:
            response = self.sns_client.publish(
                TargetArn=target_arn,
                Message=json.dumps(message),
                Subject=subject
            )
            return response.get('MessageId')
        except (BotoCoreError, ClientError) as e:
            raise SNSPublishMessageError(f"Error when it was publishing messages: {e}")


class SQSPollingMessagesError(Exception):
    """
    Exception raised for polling SQS messages error.

    Attributes:
        message -- explanation of the SQS polling message error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SQSClosingConnectionError(Exception):
    """
    Exception raised for closing SQS connection error.

    Attributes:
        message -- explanation of the SQS closing connection error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SQSDeleteMessageError(Exception):
    """
    Exception raised for deleting SQS messages error.

    Attributes:
        message -- explanation of the SQS deleting message error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SQSService:
    """
    SQSService class allows to interact with Amazon SQS (Simple Queue Service) for the hotel coupon app.
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region, aws_sqs_queue_url):
        """
        Initialize the SQS client with the provided credentials and region.

        :param aws_access_key_id: The AWS access key ID.
        :param aws_secret_access_key: The AWS secret access key.
        :param aws_region: The AWS region name.
        :param aws_sqs_queue_url: The URL of the SQS queue.
        """
        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        self.queue_url = aws_sqs_queue_url

    def delete_message(self, queue_url, receipt_handle):
        """
        Delete a message from an SQS queue.

        :param queue_url: The URL of the SQS queue.
        :param receipt_handle: The receipt handle of the message to delete.
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            print(f"Deleted message with receipt handle: {receipt_handle}")
        except (BotoCoreError, ClientError) as e:
            raise SQSDeleteMessageError(f"Error when it was deleting messages: {e}")

    def receive_messages(self, queue_url, max_messages=1, wait_time=0, visibility_timeout=30):
        """
        Receive messages from an SQS queue.

        :param queue_url: The URL of the SQS queue.
        :param max_messages: The maximum number of messages to retrieve.
        :param wait_time: The long polling wait time in seconds.
        :param visibility_timeout: The visibility timeout for messages in seconds.
        """
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                VisibilityTimeout=visibility_timeout
            )
            return response.get('Messages', [])
        except (BotoCoreError, ClientError) as e:
            print(f"Error when it was receiving messages: {e}")
            return []

    def poll_messages(self, message_handler, target_message_count=10, wait_time=10, max_messages=10,
                      visibility_timeout=30):
        """
        Polls messages from the SQS queue until a specific number of messages is retrieved or the queue is empty.

        :param message_handler: Function to process each message.
        :param target_message_count: The target number of messages to retrieve before stopping.
        :param wait_time: Long polling wait time in seconds.
        :param max_messages: Maximum number of messages to retrieve in each poll.
        :param visibility_timeout: Visibility timeout for messages in seconds.
        """
        collected_messages = 0  # Counter to track the number of processed messages

        while collected_messages < target_message_count:
            try:
                # Adjust the number of messages to request in each poll based on the remaining target
                remaining_messages = target_message_count - collected_messages
                messages_to_fetch = min(max_messages, remaining_messages)

                messages = self.receive_messages(self.queue_url, messages_to_fetch, wait_time, visibility_timeout)
                # If no more messages are in the queue, break out of the loop
                if not messages:
                    print("No more messages in the queue.")
                    break

                # Process each message and keep track of successfully processed messages
                for message in messages:
                    receipt_handle = message['ReceiptHandle']
                    success = message_handler(message)

                    # If message is processed successfully, delete it and update the count
                    if success:
                        try:
                            self.delete_message(self.queue_url, receipt_handle)
                            collected_messages += 1
                            print(f"Message {message['MessageId']} processed and deleted.")
                        except SQSDeleteMessageError as e:
                            print(f"Error when it was deleting message {message['MessageId']}: {e}")
                    else:
                        print(f"Failed to process message {message['MessageId']}.")

                    # Stop if we reach the target message count
                    if collected_messages >= target_message_count:
                        print(f"Reached target of {target_message_count} messages. Stopping.")
                        return

            except (BotoCoreError, ClientError) as e:
                print(f"Error receiving or processing messages: {e}")
                time.sleep(5)

    def close(self):
        """
        Close the SQS client to release resources.
        """
        try:
            self.sqs_client.close()
            print("SQS client closed successfully.")
        except Exception as e:
            raise SQSClosingConnectionError(f"Error when it was closing SQS client: {e}")