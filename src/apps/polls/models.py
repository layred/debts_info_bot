from django.db import models  # noqa
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Creditor(models.Model):

    user = models.ForeignKey('bot.TelegramUser', verbose_name=_('Пользователь телеграмма'), on_delete=models.CASCADE)
    name = models.CharField(_('Имя кредитора'), max_length=255)

    class Meta:
        verbose_name = 'Кредитор'
        verbose_name_plural = 'Кредитор'

    def __str__(self):
        return self.name

    def total_debt(self):
        return sum([credit.total_amount for credit in self.credit_set.all()])


class Credit(models.Model):

    creditor = models.ForeignKey('polls.Creditor', verbose_name=_('Кредитор'), on_delete=models.CASCADE)
    amount = models.IntegerField(_('Сумма кредита/займа'))
    total_amount = models.DecimalField(_('Сумма на текущий день'), max_digits=7, decimal_places=2, editable=False, default=0.00)
    bet = models.IntegerField(_('% Ставка в год'))
    register_date = models.DateTimeField(_('Дата оформления'), auto_now=False, auto_now_add=False)
    return_date = models.DateTimeField(_('Дата возврата'), auto_now=False, auto_now_add=False)
    comment = models.TextField(_('Комментарий'))

    class Meta:
        verbose_name = 'Кредит/Займ'
        verbose_name_plural = 'Кредиты/Займы'

    def update_total_amount(self):
        self.total_amount = round(self.amount + self.get_percents(), 2)
        self.save()

    def get_percents(self):
        return self.amount * ((self.bet / 365) / 100) * (timezone.now() - self.register_date).days
        # return self.amount * ((timezone.now() - self.register_date).days / 365) * self.bet

    def __str__(self):
        return f'{self.creditor.name}. {self.amount}'
