/**
 * Data that gets populated into the form.
 * @typedef {Object} FormData
 * @property {?number} project
 * @property {?boolean} isBillable
 * @property {?boolean} isExcluded
 * @property {number} project_allocation
 * @property {number} hours
 */

/** @function
 * Pulls data from the form
 * @name getFormData
 * @returns {FormData[]}
 *
 * */
function getFormData() {
  let data = []
  Array.from(document.querySelectorAll('.entry')).forEach((entry, i) => {
    const markedForDeletion = entry.querySelector('.entry-delete input').checked

    if (markedForDeletion) {
      return;
    }
    const project =
      parseInt(entry.querySelector('.entry-project select').value, 10) || null;
    const isExcluded = project
      ? excludedFromBillability.includes(project)
      : null;
    const isBillable = project
      ? !isExcluded && !nonBillableProjects.includes(project)
      : null;
    const hours =
      parseFloat(entry.querySelector('.entry-amount input').value) || 0.0;
   const project_allocation =
      parseFloat(entry.querySelector('.entry-project_allocation select').value) || 0.0;

    data.push({ project, isBillable, isExcluded, hours, project_allocation });
  });

  return data
}

/** @function
 * @name roundToNearestHalf
 * @param {number} number
 * @returns {number}
 *
 * */
function roundToNearestHalf(number) {
  return Math.ceil(number * 2) / 2;
}

/** @function
 * Rounds to two decimal places
 * @name round
 * @param {number} number
 * @returns {number}
 *
 * */
function round(number) {
  return parseFloat(number.toFixed(2));
}

/**
 * Data about hours and billable expectations.
 * @typedef {Object} HoursReport
 * @property {number} totalHours
 * @property {number} excludedHours
 * @property {number} nonBillableHours
 * @property {number} billableHours
 */

/** @function
 * Calculates data about billable hours
 * @name getHoursReport
 * @returns {HoursReport}
 * */
function getHoursReport() {
  const data = getFormData();
  // console.log("data")
  // console.log(data)
  data.forEach(calcAllocationHours)
  const r = data.reduce(
    (sums, entry) => {
      if (!entry) return sums

      sums.totalHours += entry.hours;
      if (entry.isExcluded) sums.excludedHours += entry.hours;
      if (entry.isBillable) sums.billableHours += entry.hours;

      return sums;
    },
    {
      totalHours: 0,
      excludedHours: 0,
      billableHours: 0,
    }
  );

  // Round user input to .01; round system to .5
  return {
    totalHours: round(r.totalHours),
    excludedHours: round(r.excludedHours),
    nonBillableHours: round(r.totalHours - r.billableHours - r.excludedHours),
    billableHours: round(r.billableHours),
    billableHoursTarget: roundToNearestHalf(
      (totalHoursTarget - r.excludedHours) * billableExpectation
    ),
  };
}

/** @function
 * Calcuate the hours to validate the project allocation
 * @name calcAllocationHours
 * */

function calcAllocationHours(data) {
  if (data.project_allocation > 0){
    data.hours = (data.project_allocation * (billableExpectation * totalHoursTarget))
  }
}
/** @function
 * Populates hour totals and fills in icons
 * @name populateHourTotals
 * */
function populateHourTotals() {
  // Populate The Bottom Addon Items with Totals
  const totals = getHoursReport();
  const totalElement = document.querySelector('.entries-total-reported-amount');
  const billableElement = document.querySelector(
    '.entries-total-billable-amount'
  );

  totalElement
    .querySelector('.fill')
    .setAttribute(
      'stroke-dasharray',
      `${totals.totalHours / totalHoursTarget} 1`
    );

  billableElement
    .querySelector('.fill')
    .setAttribute(
      'stroke-dasharray',
      `${totals.billableHours / totals.billableHoursTarget} 1`
    );

  totalElement.querySelector('.number-label').innerHTML = totals.totalHours;
  billableElement.querySelector('.number-label').innerHTML =
    totals.billableHours;

  if (totals.totalHours === 0) {
    totalElement.classList.remove('valid', 'invalid');
  } else if (totals.totalHours === totalHoursTarget) {
    totalElement.classList.add('valid');
    totalElement.classList.remove('invalid');
  } else {
    totalElement.classList.add('invalid');
    totalElement.classList.remove('valid');
  }

  if (totals.billableHours === 0) {
    billableElement.classList.remove('valid', 'invalid');
  } else if (
    totals.billableHours >= totals.billableHoursTarget &&
    totals.totalHours <= totalHoursTarget
  ) {
    billableElement.classList.add('valid');
    billableElement.classList.remove('invalid');
  } else {
    billableElement.classList.add('invalid');
    billableElement.classList.remove('valid');
  }
}

/** @function
 * Toggles the notes field on if the project requires them
 * @name toggleNotesField
 * @param {string} selectBoxId
 * */
function toggleNotesField(selectBoxId) {
  const idx = selectBoxId.match(/\d/)[0];
  const notes = document.querySelector('#id_timecardobjects-' + idx + '-notes')
    .parentElement;
  const options = document.querySelector('#' + selectBoxId + '-select')
    .selectedOptions[0].dataset;
  if (options.notesDisplayed === 'true' || options.notesRequired === 'true') {
    notes.classList.remove('entry-hidden');
  } else {
    notes.classList.add('entry-hidden');
  }
}

/** @function
 * Toggles the hours to project allocation on if the project requires them
 * @name toggleHoursField
 * @param {string} selectBoxId
 * */
 function toggleHoursField(selectBoxId) {
  const idx = selectBoxId.match(/\d/)[0];
  const project_allocation = document.querySelector('#id_timecardobjects-' + idx + '-project_allocation')
    .parentElement;
  const project_allocation_set = document.querySelector('#id_timecardobjects-' + idx + '-project_allocation')
  const hours_set = document.querySelector('#id_timecardobjects-' + idx + '-hours_spent')
  const hours_spent = document.querySelector('#id_timecardobjects-' + idx + '-hours_spent')
    .parentElement;
  const options = document.querySelector('#' + selectBoxId + '-select')
    .selectedOptions[0].dataset;
  if (options.is_weekly_bill === 'true') {
    project_allocation.classList.remove('entry-hidden');
    hours_spent.classList.add('entry-hidden');
  } else {
    project_allocation.classList.add('entry-hidden');
    hours_spent.classList.remove('entry-hidden');
    project_allocation_set.selectedIndex = -1;
  }
}

/** @function
 * Populates and displays and alerts attached to the project
 * @name displayAlerts
 * @param {string} selectBoxId
 * */
function displayAlerts(selectBoxId) {
  const alertElement = document
    .querySelector('#' + selectBoxId + '-select')
    .parentElement.querySelector('.entry-alerts');
  const alerts = document.querySelector('#' + selectBoxId + '-select')
    .selectedOptions[0].dataset.alerts;

  // clear out prior alerts
  while (alertElement.firstChild) {
    alertElement.removeChild(alertElement.firstChild);
  }

  if (alerts === undefined) {
    return;
  }

  // TODO: fix the JSON on the python end so we don't need this double parse
  alertData = JSON.parse(JSON.parse('"' + alerts + '"'));

  for (var i = 0; i < alertData.length; i++) {
    alert_text = alertData[i].text;

    if (alertData[i].url !== '' && alertData[i].url !== undefined) {
      alert_text =
        '<a href="' +
        alertData[i].url +
        '" target="_blank">' +
        alert_text +
        '</a>';
    }

    alertElement.innerHTML +=
      '<div class="' + alertData[i].style + '">' + alert_text + '</div>';
  }
}

/** @function
 * Adds new empty entry to the end of the list
 * @name addEntry
 * */
function addEntry() {
  const entries = document.querySelectorAll('div.entry');
  let newEntry = entries[entries.length - 1].cloneNode(true);

  // remove display: none style
  newEntry.querySelector('select').style.display = '';

  let non_checkbox_fields = newEntry.querySelectorAll('input:not([type="checkbox"]), select, textarea');
  // remove values for fields we've cloned
  for (f of non_checkbox_fields) {
      f.value = '';
  }
  // Uncheck the cloned Delete input
  newEntry.querySelector('.entry-delete input').checked = false

  newEntry.querySelector('.autocomplete__wrapper').remove();

  const previousNumber = parseInt(newEntry.getAttribute('id').match(/\d+/)[0]);
  const nextNumber = entries.length;

  if (nextNumber % 2 == 0) {
    newEntry.classList.add('even');
    newEntry.classList.remove('odd');
  } else {
    newEntry.classList.add('odd');
    newEntry.classList.remove('even');
  }

  newEntry.setAttribute('id', 'entry-' + nextNumber);

  newEntry
    .querySelectorAll('input, select, textarea, label')
    .forEach(function (formItem, i, arr) {
      if (formItem.tagName.toLowerCase() !== 'label') {
        let formerID = formItem.getAttribute('id');
        // we need the input not to have the `-select` on the id -- it interferes with the accessible
        // autocomplete library
        let nextID = formerID
          .replace(previousNumber, nextNumber)
          .replace('-select', '');
        formItem.setAttribute('id', nextID);

        let formerName = formItem.getAttribute('name');
        let nextName = formerName.replace(previousNumber, nextNumber);
        formItem.setAttribute('name', nextName);
      } else {
        let formerFor = formItem.getAttribute('for');
        let nextFor = formerFor.replace(previousNumber, nextNumber);
        formItem.setAttribute('for', nextFor);
      }
    });

  document.querySelector('.entries').appendChild(newEntry);

  accessibleAutocomplete.enhanceSelectElement({
    showAllValues: true,
    defaultValue: '',
    selectElement: newEntry.querySelector('select'),
    onConfirm: handleConfirm,
  });

  // Increment the TOTAL_FORMS value as we add lines
  // This field is necessary for Django's ManagementForm.
  // Should equal the number of `timecardobjects-#` values in the POSTed form data
  // For more information, see:
  // https://docs.djangoproject.com/en/2.2/topics/forms/formsets/#understanding-the-managementform
  document.querySelector('#id_timecardobjects-TOTAL_FORMS').value++
}

/** @function
 * When a project is changed, redo hour totals, check notes field and display alerts
 * @name updateDisplays
 * @param {string} targetId
 * */
function updateDisplays(targetId) {
  populateHourTotals();
  toggleNotesField(targetId);
  toggleHoursField(targetId);
  displayAlerts(targetId);
}

/** @function
 * Make sure autoAccessible select is correctly selected
 * @name handleConfirm
 * @param {string} val
 * */
function handleConfirm(val) {
  // there is a fun race condition where the autocomplete select is not updated!
  // before updating the displays we have to ensure that the correct option is selected.
  if (val) {
    const optValue = val.match(/\d+ -/)[0].replace(' -', '');
    const idx = this.selectElement.querySelector(`option[value='${optValue}']`)
      .index;

    this.selectElement.selectedIndex = idx;

    updateDisplays(this.id);
  }
}

/** @function
 * Show or hide the billing hour summation elements in the footer
 * @name setHourSummationVisibility
 * @param {string} visibility
 * */
function setHourSummationVisibility(visibility) {
  const showBillingHourSummationElements = visibility === 'show';
  const [totalReportedElement, totalBillableElement] = Array.from(document.querySelectorAll('.entries-total .grid-col-2'));

  if (showBillingHourSummationElements) {
    totalReportedElement.classList.remove('entry-hidden');
    totalBillableElement.classList.remove('entry-hidden');
  } else {
    totalReportedElement.classList.add('entry-hidden');
    totalBillableElement.classList.add('entry-hidden');
  }
}

//////////////////////////////////////////////////////////////
// EVENT HANDLERS

// when the hour totals are changed, repopulate hours.
document.querySelector('body').addEventListener('keyup', function (event) {
  if (
    event.target.matches('.entry-amount input')
    // Note: If you are curious how we updated project allocation, see forms.py, TimecardObjectForm, project_allocation 
    ) {
    populateHourTotals();
  }
});

// when an entry is deleted or a project is changed
document.querySelector('body').addEventListener('click', function (event) {
  if (
    event.target.matches('.entry-delete input') ||
    event.target.matches('.entry-amount input') 
  ) {
    populateHourTotals();
  }
});

// Disable scrolling in numeric input form fields from the mouse wheel or touchpad.
// Adapted from https://stackoverflow.com/questions/9712295/disable-scrolling-on-input-type-number
document.addEventListener('wheel',
  function (e) {
    if (document.activeElement.type === 'number') {
      e.preventDefault();
    }
  },
  { passive: false }
);

// On page load:
document.addEventListener('DOMContentLoaded', () => {
  document
    .getElementById('save-timecard')
    .addEventListener('click', function () {
      // TODO: This feels like it should be rendered by the Django templates, not dynamically added.
      const form = document.querySelector('form');
      const save_input = document.createElement('input');
      save_input.setAttribute('type', 'hidden');
      save_input.setAttribute('name', 'save_only');
      save_input.setAttribute('value', '1');
      form.appendChild(save_input);
      form.submit();
    });

  document
    .getElementById('submit-timecard')
    .addEventListener('click', function () {
      document.querySelector('form').submit();
    });

  document
    .querySelector('.add-timecard-entry')
    .addEventListener('click', addEntry);

  populateHourTotals();

  // adds accessible autocomplete to existing <select> fields
  const selects = document.querySelectorAll('.entry-project select');
  selects.forEach((select) => {
    accessibleAutocomplete.enhanceSelectElement({
      showAllValues: true,
      defaultValue: '',
      selectElement: select,
      onConfirm: handleConfirm,
    });

    // make sure any necessary notes or alerts are present
    updateDisplays(select.id.replace('-select', ''));
  });
});
