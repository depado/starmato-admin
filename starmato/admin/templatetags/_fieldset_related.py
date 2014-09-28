# -*- coding: utf-8 -*-
def before_related(adminform):
    adminform.fieldsets_before = adminform.fieldsets
    adminform.fieldsets_after = []
    try:
        adminform.fieldsets_before = adminform.fieldsets[:adminform.fieldsets.index(('related_go_here', {'fields': []}))]
        adminform.fieldsets_after = adminform.fieldsets[adminform.fieldsets.index(('related_go_here', {'fields': []}))+1:]
        adminform.fieldsets = adminform.fieldsets_before
        return adminform
    except:
        return adminform

def after_related(adminform):
    try:
        adminform.fieldsets = adminform.fieldsets_after
        adminform.fieldsets_before = adminform.fieldsets[:adminform.fieldsets.index(('related_go_here', {'fields': []}))]
        adminform.fieldsets_after = adminform.fieldsets[adminform.fieldsets.index(('related_go_here', {'fields': []}))+1:]
        adminform.fieldsets = adminform.fieldsets_after
        return adminform
    except:
        return adminform

