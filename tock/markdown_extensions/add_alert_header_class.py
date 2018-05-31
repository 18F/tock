import re


def set_alert_heading_class(self, element):
    for child in element:
        if re.search('h\d', child.tag, re.IGNORECASE):
            child.set('class', 'usa-alert-heading')
        set_alert_heading_class(child)
