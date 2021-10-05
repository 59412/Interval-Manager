import json
import requests
import sqlite3
import uuid

from celery import shared_task
from django.http import HttpResponse, HttpResponseBadRequest

from interval_manager.utils.sqlite_util import query_time_from_uuid, update_table_with_uuid, DATABASE_LINK
from interval_manager.utils.time_utils import time_displayer, get_current_time, epoch_to_date


@shared_task
def send_notification_to_webhook(
        interval_id: str,
        default_end_time: int) -> None:
    """Sends timer completion message to provided webhook if timer is completed"""
    (start_time, end_time, _, webhook_url) = query_time_from_uuid(interval_id)

    # if end_time != default_end_time, then we've paused this task at least once
    # and the newer instance of this task from next resume function should send
    # the message instead
    if end_time == default_end_time:
        requests.post(
            webhook_url,
            data=json.dumps(
                {
                    "text": f"Your requested timer {interval_id} has reached its end!"
                            f"Started at: {epoch_to_date(start_time)}"
                            f"Ended at: {epoch_to_date(end_time)}"
                 }
            ),
            headers={'Content-Type': 'application/json'}
        )


def create_interval_request_handler(
        request,
        duration: int,
        webhook_url: str) -> HttpResponse:
    """Creates a new timer with requested duration (in milliseconds) & webhook url,
    returns the uuid back as HttpResponse"""
    new_uuid = str(uuid.uuid4())

    curr_time = get_current_time()
    end_time = curr_time + duration

    con = sqlite3.connect(DATABASE_LINK)
    cur = con.cursor()

    # create DB row (uid, start_time, end_time, remain_time, webhook_url) =
    # (new_uuid, curr_time, end_time, None, webhook_url)
    cur.execute(
        "INSERT INTO intervals VALUES (?, ?, ?, ?, ?)",
        (new_uuid, curr_time, end_time, 0, webhook_url)
    )
    con.commit()
    con.close()

    # create Celery task instance here
    send_notification_to_webhook.apply_async(
        args=[new_uuid, end_time],
        countdown=duration/1000,
    )

    return HttpResponse(f"New interval with ID: {new_uuid} created")


def check_status_request_handler(
        request,
        interval_id: str) -> HttpResponse:
    """Report status of the timer with requested uuid"""
    (start_time, end_time, remain_time, _) = query_time_from_uuid(interval_id)

    assert not (end_time and remain_time)
    curr_time = get_current_time()
    if remain_time:
        return HttpResponse(
            f"The timer you are looking for is currently "
            f"paused with {time_displayer(remain_time)} left"
        )
    elif end_time < curr_time:
        return HttpResponse(
            f"The timer you are looking for finished on {epoch_to_date(end_time)}"
        )
    else:
        curr_remain_time = end_time - curr_time
        return HttpResponse(
            f"The timer still has {time_displayer(curr_remain_time)} left "
            f"and will finish on {epoch_to_date(end_time)}"
        )


def pause_interval_request_handler(
        request,
        interval_id: str) -> HttpResponse:
    """Pauses the timer with requested uuid"""
    (start_time, end_time, remain_time, _) = query_time_from_uuid(interval_id)

    if remain_time:
        return HttpResponse(
            f"Timer {interval_id} is already paused with "
            f"{time_displayer(remain_time)} left"
        )
    curr_time = get_current_time()
    remain_time = end_time - curr_time
    if remain_time < 0:
        return HttpResponseBadRequest(
            f"Invalid pause request, timer {interval_id} has already completed"
        )

    update_table_with_uuid(interval_id, 0, remain_time)

    return HttpResponse(
            f"Timer {interval_id} paused with {time_displayer(remain_time)} left"
        )


def resume_interval_request_handler(
        request,
        interval_id: str) -> HttpResponse:
    """Resumes the timer with requested uuid"""
    (start_time, end_time, remain_time, webhook_url) = query_time_from_uuid(interval_id)

    if not remain_time:
        return HttpResponse(
            f"Timer {interval_id} is currently running, "
            f"ends on {epoch_to_date(end_time)}"
        )
    curr_time = get_current_time()
    end_time = curr_time + remain_time

    update_table_with_uuid(interval_id, end_time, 0)
    send_notification_to_webhook.apply_async(
        args=[interval_id, end_time],
        countdown=remain_time,
    )

    return HttpResponse(
        f"Timer {interval_id} has been resumed and will stop on "
        f"{epoch_to_date(end_time)}"
    )
