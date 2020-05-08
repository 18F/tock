(function () {
  const unfiledTimecardFilter = document.getElementById('unfiled-timecards-org-filter-select');
  const unfiledTimecardTable = document.getElementById('js-unfiled-timecards');
  const rows = unfiledTimecardTable.getElementsByTagName('tr');

  const showRow = (row) => {
    row.style.display = 'table-row';
  };

  const hideRow = (row) => {
    row.style.display = 'none';
  };

  const filterByOrg = (selectedOrg) => {
    for (i in rows) {
      // skip the header row, which contains `th`, and other gunk
      try {
        const org = rows[i].getElementsByTagName('td')[3];
        if (org.innerText !== selectedOrg) {
          hideRow(rows[i]);
        } else {
          showRow(rows[i]);
        }
      } catch (err) {
        console.log(err);
      }
    }
  };

  unfiledTimecardFilter.addEventListener('change', (e) => {
    let selectedOrg = e.target.value;
    switch (selectedOrg) {
      case 'all':
        for (i in rows) {
          showRow(rows[i]);
        }
        break;
      case 'None':
        // 'None' shows up as a blank cell in the table
        filterByOrg('');
        break;
      default:
        filterByOrg(selectedOrg);
    }
  });
})(window);