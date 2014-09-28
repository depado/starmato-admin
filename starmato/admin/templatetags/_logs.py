# -*- coding: utf-8 -*-
from django.contrib.admin.models import LogEntry
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

def logs(obj):
    try:
        logs = LogEntry.objects.filter(object_id=obj.id).order_by('-action_time')
        created = logs.filter(action_flag=1)
        modified = logs.filter(action_flag=2)

        output = []
        if created.count():
            output.append(u"%s : %s" % (_("Created on:"), created[0].action_time.strftime('%d/%m/%Y')))
        else:
            output.append(u"%s" % _("Imported from former database"))
        if modified.count():
            output.append(" - ")
            output.append(u"%s %s" % (_("Modified on:"), modified[0].action_time.strftime('%d/%m/%Y')))
        return mark_safe(u" ".join(output))
    except:
        return u""
