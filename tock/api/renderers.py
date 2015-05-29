from rest_framework_csv.renderers import CSVRenderer, CSVStreamingRenderer

# This class is needed to extract the "results" list from paginated data.
# see: https://github.com/mjumbewu/django-rest-framework-csv#pagination
class PaginatedCSVRenderer(CSVRenderer):
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])

        # rest_framework_csv does this the wrong way: it creates a set() of all
        # the data elements' keys and sorts them ascending. Assuming that the
        # data is a list of dicts, this should produce a sensible list of
        # column headers
        if not self.headers and len(data) > 0:
            self.headers = data[0].keys()
        return super(PaginatedCSVRenderer, self).render(data, media_type, renderer_context)

class StreamingCSVRenderer(CSVStreamingRenderer):
    pass
