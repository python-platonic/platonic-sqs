from datetime import timedelta

import contexttimer
import pytest
from platonic.queue import MessageReceiveTimeout
from platonic.sqs.queue import SQSReceiver, SQSSender
from platonic.timeout import ConstantTimeout
from tests.test_queue.robot import Command, ReceiverAndSender


def test_empty_queue(receiver_and_sender: ReceiverAndSender):
    """Empty queue leads to waiting for a while and empty response."""
    receiver, _sender = receiver_and_sender
    receiver.timeout = ConstantTimeout(period=timedelta(seconds=1))

    with contexttimer.Timer() as timer:
        with pytest.raises(MessageReceiveTimeout):
            receiver.receive()

        elapsed_time = timer.elapsed

    assert round(elapsed_time) >= 1, 'We have waited for 1 second at least.'


def test_non_empty_queue(receiver_and_sender: ReceiverAndSender):
    """Non empty queue leads to immediate response."""
    receiver, sender = receiver_and_sender
    receiver.timeout = ConstantTimeout(period=timedelta(seconds=10))

    sender.send_many([Command.JUMP, Command.RIGHT])

    with contexttimer.Timer() as timer:
        assert receiver.receive().value == Command.JUMP
        assert receiver.receive().value == Command.RIGHT

        elapsed_time = timer.elapsed

    assert elapsed_time < 1


def test_empty_queue_and_receive(
    str_receiver_with_constant_timeout: SQSReceiver,
):
    """Wait for a while."""
    with contexttimer.Timer() as timer:
        with pytest.raises(MessageReceiveTimeout):
            str_receiver_with_constant_timeout.receive()

        elapsed_time = timer.elapsed

    assert elapsed_time > 24
    assert elapsed_time < 26


def test_empty_queue_and_iter(str_receiver_with_constant_timeout: SQSReceiver):
    """Iterate over an empty queue."""
    with contexttimer.Timer() as timer:
        assert not list(str_receiver_with_constant_timeout)
        elapsed_time = timer.elapsed

    assert elapsed_time > 24
    assert elapsed_time < 26


def test_send_and_iterate_with_timeout(
    str_receiver_with_constant_timeout: SQSReceiver,
    str_sender: SQSSender,
):
    str_sender.client.purge_queue(
        QueueUrl=str_sender.url,
    )
    str_sender.send('buzinga')

    with contexttimer.Timer() as timer:
        messages = list(str_receiver_with_constant_timeout)
        elapsed_time = timer.elapsed

    assert len(messages) == 1
    assert messages[0].value == 'buzinga'

    assert elapsed_time > 24
    assert elapsed_time < 26

    str_receiver_with_constant_timeout.acknowledge(messages[0])
