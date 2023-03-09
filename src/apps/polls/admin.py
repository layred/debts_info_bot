from apps.polls.models import Credit, Creditor
from django.contrib import admin  # noqa


# Register your models here.
class CreditInline(admin.StackedInline):
    model = Credit
    extra = 1
    show_change_link = True


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('creditor', 'comment', 'amount', 'total_amount', )


@admin.register(Creditor)
class CreditorAdmin(admin.ModelAdmin):
    inlines = (CreditInline, )
    list_display = ('name', 'total_debt', )
