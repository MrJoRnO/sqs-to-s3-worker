import re
from unittest.mock import MagicMock, patch

import pytest

from src.main import receive_message, save_to_s3, delete_message, main


FAKE_RECEIPT = "fake-receipt-handle"
FAKE_BODY = "I want to be in CloudTeam :)"


# ── receive_message ────────────────────────────────────────────────────────────

def test_receive_message_returns_message():
    sqs = MagicMock()
    sqs.receive_message.return_value = {
        "Messages": [{"Body": FAKE_BODY, "ReceiptHandle": FAKE_RECEIPT}]
    }
    msg = receive_message(sqs)
    assert msg["Body"] == FAKE_BODY


def test_receive_message_exits_when_queue_empty():
    sqs = MagicMock()
    sqs.receive_message.return_value = {}  # no "Messages" key

    with pytest.raises(SystemExit) as exc:
        receive_message(sqs)

    assert exc.value.code == 0


# ── save_to_s3 ─────────────────────────────────────────────────────────────────

def test_save_to_s3_key_format():
    s3 = MagicMock()
    key = save_to_s3(s3, FAKE_BODY)

    # Key must match YYYY-MM-DD-HH-MM-SS.txt
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.txt", key)


def test_save_to_s3_calls_put_object():
    s3 = MagicMock()
    save_to_s3(s3, FAKE_BODY)

    s3.put_object.assert_called_once()
    call_kwargs = s3.put_object.call_args.kwargs
    assert call_kwargs["Body"] == FAKE_BODY.encode("utf-8")


# ── delete_message ─────────────────────────────────────────────────────────────

def test_delete_message_called_with_receipt():
    sqs = MagicMock()
    delete_message(sqs, FAKE_RECEIPT)

    sqs.delete_message.assert_called_once_with(
        QueueUrl="https://sqs.eu-central-1.amazonaws.com/123456789/test-queue",
        ReceiptHandle=FAKE_RECEIPT,
    )


# ── main ───────────────────────────────────────────────────────────────────────

def test_main_happy_path():
    sqs = MagicMock()
    s3 = MagicMock()

    sqs.receive_message.return_value = {
        "Messages": [{"Body": FAKE_BODY, "ReceiptHandle": FAKE_RECEIPT}]
    }

    with patch("src.main.boto3") as mock_boto3:
        mock_boto3.client.side_effect = lambda service: sqs if service == "sqs" else s3
        main()

    s3.put_object.assert_called_once()
    sqs.delete_message.assert_called_once()
