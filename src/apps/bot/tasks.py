from apps.bot.management.commands.bot import bot
from apps.bot.models import TelegramUser
from core.celery import app


@app.task(name='Send debt notification')
def send_debt_notification():
    for user in TelegramUser.objects.all():
        for creditor in user.creditor_set.all():
            for credit in creditor.credit_set.all():
                credit.update_total_amount()

    for user in TelegramUser.objects.all():
        bot.send_debt_notification(user)
