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
                    onclick="download_table_as_csv('{generated_id}-table', '{name_hint}')"
                >Export CSV</button>
            </div>
            <div class="usa-table-container--scrollable grid-row" tabindex=0>
                """ + frame.to_html(
                    justify="center",
                    classes="usa-table usa-table--compressed",
                    table_id=generated_id + '-table',
                    na_rep=''
                ) + """
            </div>
          </div>
        </div>
        """
    )
