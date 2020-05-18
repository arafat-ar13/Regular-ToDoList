import os
from django import template
 
register = template.Library()
 
@register.filter
def getfilename(value):
    return os.path.basename(value.file.name)