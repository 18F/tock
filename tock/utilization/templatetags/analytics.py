from django import template
register = template.Library()

from django.utils.crypto import get_random_string

@register.simple_tag
def df_table(frame, name_hint):
    generated_id = get_random_string(5)
    table_rows = ""
    table_headers = f"""
                        <th scope="col">{frame.index.name}</th>"""
    for col in frame.columns:
        table_headers += f"""
                        <th scope="col">{col}</th>"""
    for rowdata in frame.itertuples():
        table_rows += """
                    <tr>"""
        for index, celldata in enumerate(rowdata):
            if index == 0:
                table_rows += f"""
                        <th scope="row">{celldata}</th>"""
            else:
                table_rows += f"""
                        <td>{celldata}</td>"""
        table_rows += """
                </tr>"""

    return (
        f"""
        <div class="usa-accordion usa-accordion--bordered">
            <h4 class="usa-accordion__heading">
            <button class="usa-accordion__button"
                aria-expanded="false"
                aria-controls="{generated_id}">
                Data Table
            </button>
            </h4>
            <div id="{generated_id}" class="usa-accordion__content grid-container">
            <div class="grid-row">
                <button
                    class="usa-button usa-button--base float-right margin-bottom-1"
                    data-csv data-csv-id="table-{generated_id}" data-csv-name="{name_hint}"
                >Export CSV</button>
            </div>
            <div class="usa-table-container--scrollable grid-row" tabindex=0>
            <table border="1" class="dataframe usa-table usa-table--compressed" id="table-{generated_id}">
                <thead>
                    <tr style="text-align: center;">
                    {table_headers}
                    </tr>
                </thead>
                <tbody>
                {table_rows}
                </tbody>
            </table>
            </div>
          </div>
        </div>
        """
    )

@register.simple_tag
def frame_table(frame, name_hint):
    generated_id = get_random_string(5)
    return (
        f"""
        <div class="usa-accordion usa-accordion--bordered">
            <h4 class="usa-accordion__heading">
            <button class="usa-accordion__button"
                aria-expanded="false"
                aria-controls="{generated_id}">
                Data Table
            </button>
            </h4>
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
