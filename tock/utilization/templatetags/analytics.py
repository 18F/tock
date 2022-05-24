from django import template
register = template.Library()

from django.utils.crypto import get_random_string

@register.simple_tag
def frame_table(frame, name_hint):
    generated_id = get_random_string(5)
    return (
        f"""
        <div class="usa-accordion usa-accordion--bordered">
            <h2 class="usa-accordion__heading">
            <button class="usa-accordion__button"
                aria-expanded="false"
                aria-controls="{generated_id}">
                Data Table
            </button>
            </h2>
            <div id="{generated_id}" class="usa-accordion__content grid-container">
            <div class="grid-row">
                <button
                    class="usa-button usa-button--base float-right margin-bottom-1"
                    data-csv data-csv-id="table-{generated_id}" data-csv-name="{name_hint}"
                >Export CSV</button>
            </div>
            <div class="usa-table-container--scrollable grid-row" tabindex=0>
                """ + frame.to_html(
                    justify="center",
                    classes="usa-table usa-table--compressed",
                    table_id='table-' + generated_id,
                    na_rep=''
                ) + """
            </div>
          </div>
        </div>
        """
    )
