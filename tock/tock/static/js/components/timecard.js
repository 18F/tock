function clearLocalStorage() {
  // Clear anything saved locally.
  if (window.localStorage) {
    window.localStorage.removeItem(`tock-entered-hours-${objectId}`);
  }
}

function getFormData() {
  return $('.entry').map((i, entry) => {
    const markedForDeletion = $('.entry-delete input', entry).prop('checked');

    if (markedForDeletion) {
      return;
    }

    const project = parseInt($('.entry-project select', entry).val(), 10) || null;
    const isExcluded = project ? excludedFromBillability.includes(project) : null;
    const isBillable = project ? !isExcluded && !nonBillableProjects.includes(project) : null;
    const hours = parseFloat($('.entry-amount input', entry).val()) || 0;

    return { project, isBillable, isExcluded, hours };
  }).toArray();
}

function roundToNearestHalf(number) {
  return Math.ceil(number * 2) / 2;
}

function round(number) {
  return parseFloat(number.toFixed(2));
}

function getHoursReport() {
  const data = getFormData();

  const r = data.reduce((sums, entry) => {
    sums.totalHours += entry.hours;
    if (entry.isExcluded) sums.excludedHours += entry.hours;
    if (entry.isBillable) sums.billableHours += entry.hours;

    return sums;
  }, {
    totalHours: 0,
    excludedHours: 0,
    billableHours: 0
  });

  // Round user input to .01; round system to .5
  return {
    totalHours: round(r.totalHours),
    excludedHours: round(r.excludedHours),
    nonBillableHours: round(r.totalHours - r.billableHours - r.excludedHours),
    billableHours: round(r.billableHours),
    billableHoursTarget: roundToNearestHalf((totalHoursTarget - r.excludedHours) * billableExpectation),
  };
}

function populateHourTotals() {
  // Save hours to localStorage, if available
  if (window.localStorage) {
    var hoursAsEntered = [];
    $('.entries .entry').each(function (i, entry) {
      entry = $(entry);
      var project = $('.entry-project select', entry).val();
      var hours = $('.entry-amount input', entry).val();
      if (project) {
        hoursAsEntered.push({ project: project, hours: hours });
      }
    });
    window.localStorage.setItem(`tock-entered-hours-${objectId}`, JSON.stringify(hoursAsEntered));
  }

  // Populate The Bottom Addon Items with Totals
  const totals = getHoursReport();
  const totalElement = $('.entries-total-reported-amount');
  const billableElement = $('.entries-total-billable-amount');

  $('.fill', totalElement).attr('stroke-dasharray', `${totals.totalHours / totalHoursTarget} 1`)
  $('.fill', billableElement).attr('stroke-dasharray', `${totals.billableHours / totals.billableHoursTarget} 1`)

  $('.number-label', totalElement).html(totals.totalHours);
  $('.number-label', billableElement).html(totals.billableHours);

  if (totals.totalHours === 0) {
    totalElement.removeClass('valid invalid');
  }
  else if (totals.totalHours === totalHoursTarget) {
    totalElement.addClass('valid').removeClass('invalid');
  }
  else {
    totalElement.addClass('invalid').removeClass('valid');
  }

  if (totals.billableHours === 0) {
    billableElement.removeClass('valid invalid');
  }
  else if (totals.billableHours >= totals.billableHoursTarget && totals.totalHours <= totalHoursTarget) {
    billableElement.addClass('valid').removeClass('invalid');
  }
  else {
    billableElement.addClass('invalid').removeClass('valid');
  }
}

function toggleNotesField(selectBox) {
  var $fieldset = $(selectBox).parents('.entry-project'),
    $selected = $fieldset.find(':selected'),
    $notes = $fieldset.find('.entry-note-field'),
    notesDisplayed = $selected.data('notes-displayed'),
    notesRequired = $selected.data('notes-required');

  if (notesRequired || notesDisplayed) {
    $notes.toggleClass('entry-hidden', false);
  } else {
    $notes.toggleClass('entry-hidden', true);
  }
}

function displayAlerts(selectBox) {
  var $fieldset = $(selectBox).parents('.entry-project'),
    $selected = $fieldset.find(':selected'),
    $alerts = $fieldset.find('.entry-alerts'),
    all_alerts = $selected.data('alerts'),
    alert_text;

  $alerts.empty();

  if (all_alerts !== undefined) {
    all_alerts = JSON.parse(JSON.parse('"' + all_alerts + '"'));

    for (var i = 0; i < all_alerts.length; i++) {
      alert_text = all_alerts[i].text;

      if (all_alerts[i].url !== '' && all_alerts[i].url !== undefined) {
        alert_text = '<a href="' + all_alerts[i].url + '" target="_blank">' + alert_text + '</a>';
      }

      $alerts.append(
        '<div class="' + all_alerts[i].style + '">' + alert_text + '</div>'
      );
    }
  } else {
    $alerts.empty();
  }
}

function addTockLines(tockLines) {
  // Pop off the top of the array
  var line = tockLines.shift();

  if (line) {
    if (!line.project) {
      addTockLines(tockLines);
      return;
    }

    // If the last entry box isn't empty, add a new one
    if ($('div.entry:last .entry-project select').val() !== '') {
      $(".add-timecard-entry").click();
    }

    // Wait a tick so the DOM can be updated, in case a new
    // line item entry had to be created
    setTimeout(function () {
      // Set the project and trigger a GUI update
      $("div.entry:last .entry-project select").val(line.project);

      // Set the hours and trigger a data update
      $("div.entry:last .entry-amount input").val(line.hours);
      $("div.entry:last .entry-amount input").change();

      // Go again with the remaining tock lines
      addTockLines(tockLines);
    }, 20);
  } else {
    // If we're finished processing the list of tock lines,
    // trigger a change event to update the hours total and
    // re-sync any local storage.
    $("div.entry:last select").change();
  }
}

// When you change the hours, redo the totals
$("body").on("keyup", ".entry-amount input", function () {
  populateHourTotals();
});

$("body").on("click", ".entry-amount input, .entry-delete input", function () {
  populateHourTotals();
});

// When you change a project, redo the totals
$("body").on("change", ".entry-project select", function () {
  populateHourTotals();
});


$(document).ready(function () {
  $("#save-timecard").on("click", function () {
    // Clear anything saved locally.  The server is the
    // source of truth.
    clearLocalStorage();

    var form = $('form'),
      save_input = '<input type="hidden" name="save_only" value="1" />';

    form.append(save_input);
    form.submit();
  });

  $("#submit-timecard").on("click", function () {
    // Clear anything saved locally.  The server is the
    // source of truth.
    clearLocalStorage();

    $('form').submit();
  })

  $(".add-timecard-entry").on("click", function () {
    $('div.entry:last').clone().each(function (i) {
      var entry = $(this);
      entry.find('.autocomplete__wrapper').remove();
      entry.find('.entry-alerts').empty();
      entry.find('.entry-note-field').toggleClass('entry-hidden', true);
      entry.find('.entry-note-field .invalid').remove();
      entry.find('select').show();
      entry.find('input, select, textarea').val('');
      entry.find(':checkbox').prop('checked', false);

      // Remove any existing values
      entry.val('');

      var previousNumber = parseInt(entry.attr('id').split('-')[1]);
      var nextNumber = previousNumber + 1;

      entry.attr('id', 'entry-' + nextNumber);
      nextNumber % 2 == 0 ? entry.addClass('even').removeClass('odd') :
        entry.addClass('odd').removeClass('even');

      entry.find('input, select, textarea, label').each(function (i) {
        var formItem = $(this);

        if (formItem[0].tagName.toLowerCase() !== 'label') {
          var formerID = formItem.attr('id');
          var nextID = formerID.replace(previousNumber, nextNumber);
          formItem.attr('id', nextID);

          var formerName = formItem.attr('name');
          var nextName = formerName.replace(previousNumber, nextNumber);
          formItem.attr('name', nextName);
        } else {
          var formerFor = formItem.attr('for');
          var nextFor = formerFor.replace(previousNumber, nextNumber);
          formItem.attr('for', nextFor);
        }
      });
    }).appendTo('.entries');

    accessibleAutocomplete.enhanceSelectElement({
      showAllValues: true,
      defaultValue: '',
      selectElement: document.querySelector('div.entry:last-child .entry-project select')
    });

    $('div.entry:last').find('.entry-project select')
      .on('change', function (e) {
        toggleNotesField(this);
        displayAlerts(this);
      });

    // Increment the TOTAL_FORMS
    $('#id_timecardobjects-TOTAL_FORMS').val(parseInt($('#id_timecardobjects-TOTAL_FORMS').val()) + 1);
  });

  // If there's localStorage, get hours from it and
  // populate the form
  if (window.localStorage) {
    var fromStorage = window.localStorage.getItem(`tock-entered-hours-${objectId}`);
    if (fromStorage) {
      fromStorage = JSON.parse(fromStorage);

      $('.entries .entry').each(function (i, entry) {
        entry = $(entry);
        var project = $('.entry-project select', entry).val();
        var storageIndex = fromStorage.findIndex(function (storedProject) {
          return storedProject.project === project;
        });

        if (storageIndex >= 0) {
          $('.entry-amount input', entry).val(Number(fromStorage[storageIndex].hours));
          fromStorage.splice(storageIndex, 1);
        }
      });

      // Anything still represented in "fromStorage" is a line
      // that was added to the timesheet but not saved, meaning
      // there's not a GUI element for it already. We should
      // restore those lines now.
      addTockLines(fromStorage);
    }
  }

  // Run on initial load
  populateHourTotals();

  const selects = document.querySelectorAll('.entry-project select');
  selects.forEach(select => {
    accessibleAutocomplete.enhanceSelectElement({
      showAllValues: true,
      defaultValue: '',
      selectElement: select
    })
  });

  $('.entry-project input')
    .on('change', function (e) {
      toggleNotesField(this);
      displayAlerts(this);
    });

  // Force an update to each project selection menu in case a notes field
  // needs to be re-displayed.
  $('.entry-project select').trigger('change');

  // Disable scrolling in numeric input form fields from the mouse
  // wheel or touchpad.
  // Adapted from https://stackoverflow.com/questions/9712295/disable-scrolling-on-input-type-number
  $('form').on('focus', 'input[type=number]', function (e) {
    $(this).on('mousewheel.disableScroll', function (e) {
      e.preventDefault();
    });
  });

  $('form').on('blur', 'input[type=number]', function (e) {
    $(this).off('mousewheel.disableScroll');
  });
});