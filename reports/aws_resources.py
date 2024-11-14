import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
import time
import environ

class SQSPoller:

    def __init__(self, queue_url=None, region_name=None):
        env = environ.Env()
        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY'),
            region_name=region_name or env('AWS_REGION')
        )
        self.queue_url = queue_url or env('AWS_SQS_QUEUE_URL')

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

                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=messages_to_fetch,
                    WaitTimeSeconds=wait_time,
                    VisibilityTimeout=visibility_timeout
                )

                messages = response.get('Messages', [])

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
                        self.sqs_client.delete_message(
                            QueueUrl=self.queue_url,
                            ReceiptHandle=receipt_handle
                        )
                        collected_messages += 1
                        print(f"Message {message['MessageId']} processed and deleted.")
                    else:
                        print(f"Failed to process message {message['MessageId']}.")

                    # Stop if we reach the target message count
                    if collected_messages >= target_message_count:
                        print(f"Reached target of {target_message_count} messages. Stopping.")
                        return

            except (BotoCoreError, ClientError) as e:
                print(f"Error receiving or processing messages: {e}")
                time.sleep(5)


    def purge_queue(self):
        """
        Purges all messages from the SQS queue.
        """
        try:
            self.sqs_client.purge_queue(QueueUrl=self.queue_url)
            print("Queue purged successfully.")
        except (BotoCoreError, ClientError) as e:
            print(f"Failed to purge the queue: {e}")
