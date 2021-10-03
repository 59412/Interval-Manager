from celery import Celery, shared_task
import datetime
from django.http import HttpResponse
from django.shortcuts import render
import sqlite3
import uuid

con = sqlite3.connect('intervals.db')
cur = con.cursor()

# cur.execute('''create table intervals (
#     uuid text,
#     start_time integer,
#     end_time integer,
#     remain_time integer,
#     webhook_url text
# )''')
#
# con.commit()


@shared_task
def send_notification_to_webhook(url, content):
    print(f"sending content to {url}"
          f"{content}")


def create_interval_request_handler(request, duration, webhook_url):
    try:
        new_uuid = str(uuid.uuid4())

        con = sqlite3.connect('intervals.db')
        cur = con.cursor()

        curr_time = int(datetime.datetime.now().timestamp() * 1000)

        end_time = curr_time + duration

        # create DB row (uid, start_time, end_time, remain_time, webhook_url) =
        # (new_uuid, curr_time, end_time, None, webhook_url)
        cur.execute(
            "INSERT INTO intervals VALUES (?, ?, ?, ?, ?)",
            (new_uuid, curr_time, end_time, None, webhook_url)
        )
        con.commit()
        con.close()

        # create Celery task instance here
        send_notification_to_webhook.apply_async(
            args=[webhook_url, f"{new_uuid} is completed"],
            countdown=10,
        )

        return HttpResponse(f"New interval with ID: {new_uuid} created")
    except Exception as e:
        return HttpResponse(f"{str(e)}")


def check_status_request_handler(request, interval_id):
    start_time, end_time, remain_time = ("", "", "")

    assert not (end_time and remain_time)
    if remain_time:
        return HttpResponse(f"{remain_time} left and paused")
    else:
        return HttpResponse(f"{end_time} - curr_time")


def pause_interval_request_handler(request, interval_id):
    # through query(uid), get
    start_time, end_time, remain_time = ("", "", "")
    curr_time = "get from datetime"
    remain_time = "end_time - curr_time"
    end_time = None

    # update db here


def resume_interval_request_handler(request, interval_id):
    # through query(uid), get
    start_time, end_time, remain_time = ("", "", "")
    curr_time = "get from datetime"
    end_time = "curr_time + remain_time"
    remain_time = None

    # update db here


def display_handler(request):
    return HttpResponse(f"Display page")
