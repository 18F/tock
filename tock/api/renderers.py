from rest_framework_csv.renderers import CSVRenderer
from django.http import StreamingHttpResponse

import csv

class PaginatedCSVRenderer(CSVRenderer):
    """
    This class extracts the "results" list from paginated data. See:
    <https://github.com/mjumbewu/django-rest-framework-csv#pagination>
    """
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])

        # rest_framework_csv does this the wrong way: it creates a set() of all
        # the data elements' keys and sorts them ascending. Assuming that the
        # data is a list of dicts, this should produce a sensible list of
        # column headers
        if not self.header and len(data) > 0:
            self.header = data[0].keys()
        return super(PaginatedCSVRenderer, self).render(data, media_type, renderer_context)

def stream_csv(queryset, serializer):
    """
    Stream data as CSV, given an interable queryset and a DRF
    Serializer instance with a .fields dict and .to_representation()
    method.
    """
    rows = map(serializer.to_representation, queryset.iterator())
    fields = list(serializer.fields.keys())
    return StreamingHttpResponse(generate_csv(rows, fields), content_type='text/csv')

class Echo(object):
    """
    A pseudo-buffer, see:
    <https://docs.djangoproject.com/en/1.8/howto/outputting-csv/#streaming-large-csv-files>
    """
    def write(self, value):
        return value

def generate_csv(rows, fields=None, **writer_options):
    """
    This generator yields text for each written row, and optionally
    writes a header row. We're using DictWriter.writerow() instead of
    writeheader() because the latter doesn't return a value.
    """
    buff = Echo()
    if fields:
        writer = csv.DictWriter(buff, fieldnames=fields, **writer_options)
        header = dict((field, field) for field in fields)
        yield writer.writerow(header)
    else:
        writer = csv.writer(buff, **writer_options)
    for row in rows:
        yield writer.writerow(row)
