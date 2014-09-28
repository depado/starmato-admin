# -*- coding: utf-8 -*-
import simplejson, urllib
from decimal import Decimal
#
from django.db import models
from django.utils.translation import ugettext as _

################################################################################
# static definitions of general options to handle special values and models
#       domain_name: The domain of the website
#       def_lang: The default language for the admin and the web pages
#       def_currency: The default currency for the admin and the web pages
#       def_country: The default country for the admin and the web pages
#       def_gallery: Id of the contact.Contact which is the gallery 
################################################################################
starmato_options = ['domain_name', 'project_name', 'project_logo',
                    'def_color', 'def_iconset',
                    'def_lang', 'def_currency', 'def_country',
                    ]

################################################################################
# StarmatoOption class
################################################################################
class   StarmatoOption(models.Model):
    option = models.CharField(max_length=16,            verbose_name=_(u"Option name"), help_text=_("Option name must be less than 16 characters long"))
    value =  models.CharField(max_length=200,            verbose_name=_(u"Option value"), help_text=_("Option value must be less than 200 characters long"))

    def __unicode__(self):
        return u"%s = %s" % (self.option, self.value)

    class Meta:
        verbose_name = _(u"Global option")
        verbose_name_plural = _(u"Global options")

################################################################################
# generic function to retrieve the value of an option
# Typically used at the beginning of a python file, after imports:
#   CONSTANT = get_starmato_option('key')
# can be imported in other file afterwards:
#   import CONSTANT from definitions.py
################################################################################
def get_starmato_option(ref):
    try:
        return StarmatoOption.objects.get(option=ref).value
    except:
        for option in StarmatoOption.objects.all():
            if option.option == ref:
                return option.value
    return ""

class   ForeignCharField(models.Model):
    label = models.CharField(max_length=128,             verbose_name=_(u"Label"))

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _(u"Predefined label")
        verbose_name_plural = _(u"Predefined labels")
        abstract = True

################################################################################
# Autocomplete TextInput: table to store labels
################################################################################
class   _ContactLabel(models.Model):
    label = models.CharField(max_length=24, unique=True)
    cnt = models.PositiveIntegerField(                  verbose_name=_(u"Occurrences"))

    def __unicode__(self):
        return self.label

################################################################################
# Language and country settings (fixtures exist)
################################################################################

# https://raw.github.com/currencybot/open-exchange-rates/master/latest.json
# https://raw.github.com/currencybot/open-exchange-rates/master/historical/1999-10-08.json
BASE_CURRENCY_URL = 'http://openexchangerates.org/api'
APP_ID = "de4ff0bce380484b818fc5db7d26ceee"

class   CurrencyManager(models.Manager):
    def get_query_set(self):
        return super(CurrencyManager, self).get_query_set().filter(code__in=('FRF','CHF','EUR','GBP', 'JPY', 'USD',))

class   Currency(models.Model):
    code = models.CharField(max_length=3,               verbose_name=_(u"Short name"), primary_key=True)
    name = models.CharField(max_length=32,              verbose_name=_(u"Long name"))
    symbol = models.CharField(max_length=1,             verbose_name=_(u"Symbol"), blank=True, null=True)
    rate = models.DecimalField(decimal_places=8,        verbose_name=_(u"Rate"), max_digits=20)

    objects = CurrencyManager()
    def __unicode__(self):
        if self.symbol:
           return self.symbol
        return self.code

    def get_rate(self, currency='EUR', date=None):
        if self.code == currency:
            return Decimal('1')

        try:
            to = Currency.objects.get(code=currency)
        except:
            return Decimal('0')

        if date == None:
            data = simplejson.load(urllib.urlopen('%s/%s?app_id=%s' % (BASE_CURRENCY_URL, 'latest.json', APP_ID)))
        else:
            data = simplejson.load(urllib.urlopen('%s/historical/%s.json?app_id=%s' % (BASE_CURRENCY_URL, date.strftime('%Y-%m-%d'), APP_ID)))
        try:
            return Decimal("%f" % (data['rates'][currency] / data['rates'][self.code]))
        except:
            return Decimal("%f" % (data['rates'][currency] / data['rates']['USD'])) /  self.rate
            
    class Meta:
        verbose_name = _(u"Currency")
        verbose_name_plural = _(u"Currencies")
        ordering = ["code"]

class   Language(models.Model):
    code = models.CharField(max_length=2,               verbose_name=_(u"639-1 code"), primary_key=True)
    name = models.CharField(max_length=64,              verbose_name=_(u"Name"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Language")
        verbose_name_plural = _(u"Languages")
        ordering = ["name"]

class   Country(models.Model):
    code = models.CharField(max_length=2,               verbose_name=_(u"Code"), primary_key=True)
    name = models.CharField(max_length=64,              verbose_name=_(u"Name"))
    languages = models.ManyToManyField('Language',      verbose_name=_(u"Official languages"))
    prefix = models.PositiveIntegerField(max_length=3,  verbose_name=_(u"Phone country code"))
    currency = models.ForeignKey('Currency',            verbose_name=_(u"National currency"))
    EU = models.BooleanField(default=False,             verbose_name=_(u"Member of the European Community"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")
        ordering = ["name"]
