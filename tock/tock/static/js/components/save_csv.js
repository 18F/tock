// Wait until the DOM content is loaded. In testing, it seems this script
// can be loaded before the DOM is populated, so... wait! In our case, the
// buttons remain in the DOM forever once they're loaded. This approach does
// not work if the buttons are removed from the DOM when hidden, but the
// accordions we have just hide their content when collapsed rather than
// remove it.
window.addEventListener('DOMContentLoaded', function () {
    var downloadButtons = document.querySelectorAll('button[data-csv]');

    for (var i = 0; i < downloadButtons.length; i += 1) {
        var button = downloadButtons.item(i);

        // Use an IIFE to capture variables. Otherwise all of the button events
        // will use the values from the last button, which would be wrong. A
        // classic Javascript quirk...
        (function () {
            var table_id = button.getAttribute('data-csv-id');
            var filename_prefix = button.getAttribute('data-csv-name');

            button.addEventListener('click', function () {
                download_table_as_csv(table_id, filename_prefix);
            });
        })();
    }
});

// Quick and simple export target #table_id into a csv
// inspired by https://stackoverflow.com/a/56370447
function download_table_as_csv(table_id, filename_prefix) {
    var csv_string = table_to_csv(table_id);
    download(csv_string, filename_prefix);
}

function table_to_csv(table_id) {
    // Select rows from table_id
    var rows = document.querySelectorAll('table#' + table_id + ' tr');
    // Construct csv
    var output_list = [];
    for (var i = 0; i < rows.length; i++) {
        var output_row = [];
        var cols = rows[i].querySelectorAll('td, th');

        for (var j = 0; j < cols.length; j++) {
            // Clean innertext to remove line breaks
            var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '');
            // Escape double-quote with double-double-quote
            // (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
            data = data.replace(/"/g, '""');
            // Push escaped string
            output_row.push('"' + data + '"');
        }
        output_list.push(output_row.join(','));
    }
    return output_list.join('\n');
}

function download(csv_string, filename_prefix) {
    // Download it
    var filename = filename_prefix + '_' + new Date().toLocaleDateString() + '.csv';
    var link = document.createElement('a');
    link.style.display = 'none';
    link.setAttribute('target', '_blank');
    link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv_string));
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
