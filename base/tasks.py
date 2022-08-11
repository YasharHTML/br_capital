from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from base.models import Offer
import datetime

@db_periodic_task(crontab(minute="0", hour="1", day="*", month="*", day_of_week="*"))
def check_offers():
    for offer in Offer.objects.filter(finished=False, deadline__lt=datetime.datetime.now()):
        offer.rollback()