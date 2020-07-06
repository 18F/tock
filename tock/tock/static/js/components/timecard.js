function clearLocalStorage() {
  // Clear anything saved locally.
  if (window.localStorage) {
    window.localStorage.removeItem(`tock-entered-hours-${objectId}`);
  }
}

function getFormData() {
  var ls = document.querySelectorAll('.entry');

  return Array.from(ls).map( (entry) => {
    var entry_delete = entry.querySelector('.entry-delete input');
    var markedForDeletion = entry_delete.checked;

    if (markedForDeletion) {
      return;
    }

    var project_select = entry.querySelector('.entry-project select');
    var project = parseInt(project_select.value, 10) || null;

    const isExcluded = project ? excludedFromBillability.includes(project) : null;
    const isBillable = project ? !isExcluded && !nonBillableProjects.includes(project) : null;
    
    const selector = '.entry-amount input';
    const hours = parseFloat(entry.querySelector(selector).value) || 0;
    const objToReturn = { project, isBillable, isExcluded, hours };
    return objToReturn;
  });
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
    
    var formData = getFormData();

    for (obj of formData) {
      hoursAsEntered.push({ project: obj.project, hours: obj.hours});
    }

    window.localStorage.setItem(`tock-entered-hours-${objectId}`, JSON.stringify(hoursAsEntered));
  }

  // Populate The Bottom Addon Items with Totals
  const totals = getHoursReport();
  const totalElement = document.querySelector('.entries-total-reported-amount');
  const billableElement = document.querySelector('.entries-total-billable-amount');

  totalElement.querySelector('.fill').setAttribute('stroke-dasharray', `${totals.totalHours / totalHoursTarget} 1`);
  billableElement.querySelector('.fill').setAttribute('stroke-dasharray', `${totals.billableHours / totals.billableHoursTarget} 1`);

  totalElement.querySelector('.number-label').innerHTML = totals.totalHours;
  billableElement.querySelector('.number-label').innerHTML = totals.billableHours;

  if (totals.totalHours === 0) {
    totalElement.classList.remove('valid', 'invalid');
  }
  else if (totals.totalHours === totalHoursTarget) {
    totalElement.classList.add('valid');
    totalElement.classList.remove('invalid');
  }
  else {
    totalElement.classList.add('invalid');
    totalElement.classList.remove('valid');
  }

  if (totals.billableHours === 0) {
    billableElement.classList.remove('valid', 'invalid');
  }
  else if (totals.billableHours >= totals.billableHoursTarget && totals.totalHours <= totalHoursTarget) {
    billableElement.classList.add('valid');
    billableElement.classList.remove('invalid');
  }
  else {
    billableElement.classList.add('invalid');
    billableElement.classList.remove('valid');
  }
}

function getParents(elem) {
	// Set up a parent array
	var parents = [];
	// Push each parent element to the array
	for ( ; elem && elem !== document; elem = elem.parentNode ) {
		parents.push(elem);
	}
	// Return our parent array
	return parents;
};

function getParentsBySelector(elem, selector) {
	// Element.matches() polyfill
	if (!Element.prototype.matches) {
		Element.prototype.matches =
			Element.prototype.matchesSelector ||
			Element.prototype.mozMatchesSelector ||
			Element.prototype.msMatchesSelector ||
			Element.prototype.oMatchesSelector ||
			Element.prototype.webkitMatchesSelector ||
			function(s) {
				var matches = (this.document || this.ownerDocument).querySelectorAll(s),
					i = matches.length;
				while (--i >= 0 && matches.item(i) !== this) {}
				return i > -1;
			};
	}
	// Set up a parent array
	var parents = [];
	// Push each parent element to the array
	for ( ; elem && elem !== document; elem = elem.parentNode ) {
		if (selector) {
			if (elem.matches(selector)) {
				parents.push(elem);
			}
			continue;
		}
		parents.push(elem);
	}
	// Return our parent array
	return parents;
};

function toggleNotesField(selectBox) {
  var $fieldset = $(selectBox).parents('.entry-project');
  //var $fieldset = getParents(selectBox, '.entry-project');
  var $selected = $(selectBox).find(':selected');
  var $notes = $fieldset.find('.entry-note-field');
  var notesDisplayed = $selected.data('notes-displayed');
  var notesRequired = $selected.data('notes-required');

  if (notesRequired || notesDisplayed) {
    $notes.toggleClass('entry-hidden', false);
  } else {
    $notes.toggleClass('entry-hidden', true);
  }
}

function displayAlerts(selectBox) {
  var $fieldset = $(selectBox).parents('.entry-project'),
    $selected = $(selectBox).find(':selected'),
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
      $("div.entry:last .entry-project select").trigger("chosen:updated");

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
  var chosenOptions = {
    search_contains: true,
    group_search: false
  };

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
      entry.find('.chosen-container').remove();
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

    $('div.entry:last').find('.entry-project select')
      .chosen(chosenOptions)
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

  $('.entry-project select')
    .chosen(chosenOptions)
    .on('change', function (e) {
      console.log("ENTRY PROJECT");
      console.log("e ", e);
      console.log("this ", this);
      
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