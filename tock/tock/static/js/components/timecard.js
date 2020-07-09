// FIXME 
// Rewalk the styling CSS for gray alternation...
// Magically fix with even/odd pseudoclasses.
// Get rid of the classes in alternatio in the Python
// https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-child
// with "odd"

// https://github.com/alphagov/accessible-autocomplete
// COVID FAQ or google

// CONTRACT
// clearLocalStorage :: none -> none
// PURPOSE
// Wipes out local storage in the window object for
// this tock session. Uses a magic unique ID templated in from Django.
function clearLocalStorage() {
  // Clear anything saved locally.
  if (window.localStorage) {
    window.localStorage.removeItem(`tock-entered-hours-${objectId}`);
  }
}
// CONTRACT
// getFormData :: none -> (array-of object)
// PURPOSE
// Returns an array of objects representing the subforms on the timecard page.
// Each object has four fields:
//   project :: integer or null
//   isBillable :: boolean or null
//   isExcluded :: boolean or null
//   hours :: float or zero
function getFormData() {
  var ls = document.querySelectorAll(".entry");

  return Array.from(ls).map((entry) => {
    const entry_delete = entry.querySelector(".entry-delete input");
    const project_select = entry.querySelector(".entry-project select");
    const project = parseInt(project_select.value, 10) || null;
    const isExcluded = project
      ? excludedFromBillability.includes(project)
      : null;
    const isBillable = project
      ? !isExcluded && !nonBillableProjects.includes(project)
      : null;
    const selector = ".entry-amount input";
    const hours = parseFloat(entry.querySelector(selector).value) || 0;
    const objToReturn = {
      project: project,
      isBillable: isBillable,
      isExcluded: isExcluded,
      hours: hours,
    };
    return objToReturn;
  });
}

// CONTRACT
// roundUpToNearsetHalf :: number -> number
// PURPOSE
// Given a number, round it up to the nearest half.
// EXAMPLES
// roundUpToNearestHalf(0.1) -> 0.5
function roundUpToNearestHalf(number) {
  return Math.ceil(number * 2) / 2;
}

// CONTRACT
// roundToTwoPlaces :: number -> number
// PURPOSE
// Truncates a number to two decimal places.
// EXAMPLES
// roundToTwoPlaces(0.001) -> 0
// roundToTwoPlaces(0.005) -> 0.01
// roundToTwoPlaces(0.707) -> 0.71
function roundToTwoPlaces(number) {
  return parseFloat(number.toFixed(2));
}

// CONTRACT
// getHoursReport :: none -> obj
// PURPOSE
// Total the hours for billable and excluded work from
// the entries on the page. Object returned looks like:
//   totalHours :: float (two places)
//   excludedHours :: float (two places)
//   nonBillableHours :: float (two places)
//   billableHours :: float (two places)
//   billableHoursTarget :: (rounded to nearest 0.5)
function getHoursReport() {
  const entries = getFormData();
  var totalHours = 0;
  var excludedHours = 0;
  var billableHours = 0;
  var totalHours = 0;

  for (entry of entries) {
    totalHours += entry.hours;
    if (entry.isExcluded) excludedHours += entry.hours;
    if (entry.isBillable) billableHours += entry.hours;
  }

  // Round user input to .01; round system to .5
  return {
    totalHours: roundToTwoPlaces(totalHours),
    excludedHours: roundToTwoPlaces(excludedHours),
    nonBillableHours: roundToTwoPlaces(
      totalHours - billableHours - excludedHours
    ),
    billableHours: roundToTwoPlaces(billableHours),
    billableHoursTarget: roundUpToNearestHalf(
      (totalHoursTarget - excludedHours) * billableExpectation
    ),
  };
}

function populateHourTotals() {
  // Populate The Bottom Addon Items with Totals
  const totals = getHoursReport();
  const totalElement = document.querySelector(".entries-total-reported-amount");
  const billableElement = document.querySelector(
    ".entries-total-billable-amount"
  );

  totalElement
    .querySelector(".fill")
    .setAttribute(
      "stroke-dasharray",
      `${totals.totalHours / totalHoursTarget} 1`
    );
  billableElement
    .querySelector(".fill")
    .setAttribute(
      "stroke-dasharray",
      `${totals.billableHours / totals.billableHoursTarget} 1`
    );

  totalElement.querySelector(".number-label").innerHTML = totals.totalHours;
  billableElement.querySelector(".number-label").innerHTML =
    totals.billableHours;

  if (totals.totalHours === 0) {
    totalElement.classList.remove("valid", "invalid");
  } else if (totals.totalHours === totalHoursTarget) {
    totalElement.classList.add("valid");
    totalElement.classList.remove("invalid");
  } else {
    totalElement.classList.add("invalid");
    totalElement.classList.remove("valid");
  }

  if (totals.billableHours === 0) {
    billableElement.classList.remove("valid", "invalid");
  } else if (
    totals.billableHours >= totals.billableHoursTarget &&
    totals.totalHours <= totalHoursTarget
  ) {
    billableElement.classList.add("valid");
    billableElement.classList.remove("invalid");
  } else {
    billableElement.classList.add("invalid");
    billableElement.classList.remove("valid");
  }
}

// CONTRACT
// toggleNotesField :: select element -> void
// PURPOSE
// This function walks the timecard elements and makes sure
// the notes field is present for all projects that require notes.
// This information is stored in data- attributes in the <option> elements
// of the <select> element.
function toggleNotesField(selectBox) {
  // elements is the complete "box" around a timecard entry. It is a 
  // list of elements, starting from the selectBox, walking all the way 
  // up the DOM tree.
  // The zeroth element that comes back should be the select box. 
  const elements = getParents(selectBox, ".entry-project");
  const selectedElement = elements[0];
  
  // To find out if the notes are required to be shown, we need to get the 
  // selected element, then extract data that the backend left hidden for us.
  // I start by grabbing the selected element's index, then grabbing the option element.
  const selected = selectedElement.selectedIndex;
  const opt = selectedElement.options[selectedElement.selectedIndex];

  // .text is the full text of the entry
  // .value is the numeric value of the entry (e.g. project number)
  // .attributes is a NamedNodeMap. I want data-notes-required and data-notes-displayed.
  const attributes = opt.attributes;

  // Now, walking that array until we find the entry element, which
  // we find by looking for the "entry" class.
  var entry = null;
  for (e of elements) {
    if (e.classList.contains("entry")) {
      entry = e;
      break;
    }
  }
  // This is the actual notes element that we will want to hide or show.
  var notesElement = entry.querySelector(".entry-note-field");
  
  // Find out whether or not this is an entry that must be shown.
  // The data elements are strings, so those must be compared to strings and thus
  // be converted to booleans.
  var notesRequired  = (attributes["data-notes-required"].nodeValue === "true");
  var notesDisplayed = (attributes["data-notes-displayed"].nodeValue === "true");

  // Toggle the hidden class on the notes elements.
  if (notesRequired || notesDisplayed) {
    notesElement.classList.remove("entry-hidden");
  } else {
    notesElement.classList.add("entry-hidden");
  }
}

function displayAlerts(selectBox) {
  var $fieldset = $(selectBox).parents(".entry-project"),
    $selected = $(selectBox).find(":selected"),
    $alerts = $fieldset.find(".entry-alerts"),
    all_alerts = $selected.data("alerts"),
    alert_text;

  $alerts.empty();

  if (all_alerts !== undefined) {
    all_alerts = JSON.parse(JSON.parse('"' + all_alerts + '"'));

    for (var i = 0; i < all_alerts.length; i++) {
      alert_text = all_alerts[i].text;

      if (all_alerts[i].url !== "" && all_alerts[i].url !== undefined) {
        alert_text =
          '<a href="' +
          all_alerts[i].url +
          '" target="_blank">' +
          alert_text +
          "</a>";
      }

      $alerts.append(
        '<div class="' + all_alerts[i].style + '">' + alert_text + "</div>"
      );
    }
  } else {
    $alerts.empty();
  }
}

function addTockEntry(_) {
  console.log("BUTTON TO ADD PRESSED");
  var entries = document.querySelectorAll("div.entry");
  console.log("Number of entries: " + entries.length);
  var newEntry = entries[0].cloneNode(true);

  // FIXME
  // Clean up the chosen.js bits. This will go away.
  _e = newEntry.querySelector(".chosen-container");
  _e.parentNode.removeChild(_e);
  newEntry.querySelector(".entry-note-field").classList.add("entry-hidden");

  // Remove any invalid flags.
  _e = newEntry.querySelector(".entry-note-field .invalid");
  if (_e) {
    _e.parentNode.removeChild(_e);
  }

  // Make it visible.
  newEntry.querySelector("select").style.display = "";

  // Empty the inputs.
  fields = newEntry.querySelectorAll("input, select, textarea");
  for (f of fields) {
    f.value = "";
  }
  // Remove any existing values
  newEntry.value = "";

  // Set the id for this entry. Make sure we get a new number.
  var previousNumber = parseInt(newEntry.getAttribute("id").split("-")[1]);
  var nextNumber = entries.length + 1;
  var newId = "entry-" + nextNumber;
  newEntry.setAttribute("id", newId);

  // Update the delete button.
  var button = newEntry.querySelector("#delete-entry-0");
  button.setAttribute("id", `delete-entry-${nextNumber}`);
  button.setAttribute("onclick", `removeEntry('${newId}');`);
  button.setAttribute("title", `Delete Item ${nextNumber}`);

  // Fix all the numbering on the fields.
  newEntry.querySelectorAll('input, select, textarea, label').forEach(function (el, i, arr) {
    var formItem = el;

    if (formItem.tagName.toLowerCase() !== 'label') {
      var formerID = formItem.getAttribute('id');
      var nextID = formerID.replace(previousNumber, nextNumber);
      formItem.setAttribute('id', nextID);

      var formerName = formItem.getAttribute('name');
      var nextName = formerName.replace(previousNumber, nextNumber);
      formItem.setAttribute('name', nextName);
    } else {
      var formerFor = formItem.getAttribute('for');
      var nextFor = formerFor.replace(previousNumber, nextNumber);
      formItem.setAttribute('for', nextFor);
    }
  });

  // Append the new, improved blank entry.
  document.querySelector(".entries").appendChild(newEntry);

  // Increment the TOTAL_FORMS
  // FIXME
  // Why do we have this piece of global state running around? 
  // Should this just be calculated at the point that it is needed?
  // For example, it should be set at form submission, not calculated dynamically.
  // I'm not making this change now, because I'm not sure of the implications (yet).
  const tf = parseInt(document.querySelector("#id_timecardobjects-TOTAL_FORMS").value);
  document.querySelector("#id_timecardobjects-TOTAL_FORMS").value = tf + 1;
}

//////////////////////////////////////////////////////////////
// EVENT HANDLERS
// Things that happen when things happen.

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
    group_search: false,
  };
  populateHourTotals();

  $("#save-timecard").on("click", function () {
    // Clear anything saved locally.  The server is the
    // source of truth.
    clearLocalStorage();

    var form = $("form"),
      save_input = '<input type="hidden" name="save_only" value="1" />';

    form.append(save_input);
    form.submit();
  });

  $("#submit-timecard").on("click", function () {
    // Clear anything saved locally.  The server is the
    // source of truth.
    clearLocalStorage();

    $("form").submit();
  });


  document
    .querySelector(".add-timecard-entry")
    .addEventListener("click", addTockEntry);

  // // If there's localStorage, get hours from it and
  // // populate the form
  // if (window.localStorage) {
  //   var fromStorage = window.localStorage.getItem(`tock-entered-hours-${objectId}`);
  //   if (fromStorage) {
  //     fromStorage = JSON.parse(fromStorage);

  //     $('.entries .entry').each(function (i, entry) {
  //       entry = $(entry);
  //       var project = $('.entry-project select', entry).val();
  //       var storageIndex = fromStorage.findIndex(function (storedProject) {
  //         return storedProject.project === project;
  //       });

  //       if (storageIndex >= 0) {
  //         $('.entry-amount input', entry).val(Number(fromStorage[storageIndex].hours));
  //         fromStorage.splice(storageIndex, 1);
  //       }
  //     });

  //     // Anything still represented in "fromStorage" is a line
  //     // that was added to the timesheet but not saved, meaning
  //     // there's not a GUI element for it already. We should
  //     // restore those lines now.
  //     addTockLines(fromStorage);
  //   }
  // }

  $(".entry-project select")
    .chosen(chosenOptions)
    .on("change", function (e) {
      console.log("ENTRY PROJECT");
      console.log("e ", e);
      console.log("this ", this);

      toggleNotesField(this);
      displayAlerts(this);
    });

  // Force an update to each project selection menu in case a notes field
  // needs to be re-displayed.
  $(".entry-project select").trigger("change");

  // Disable scrolling in numeric input form fields from the mouse
  // wheel or touchpad.
  // Adapted from https://stackoverflow.com/questions/9712295/disable-scrolling-on-input-type-number
  $("form").on("focus", "input[type=number]", function (e) {
    $(this).on("mousewheel.disableScroll", function (e) {
      e.preventDefault();
    });
  });

  $("form").on("blur", "input[type=number]", function (e) {
    $(this).off("mousewheel.disableScroll");
  });
});

//////////////////////////////////////////////////////////////
// HELPERS
// Utility functions.


// CONTRACT
// removeEntry :: string -> none
// PURPOSE
// Takes the ID of an entry formset, removes it, and
// updates the hour totals afterwards.
function removeEntry(elementId) {
  // Removes an element from the document
  var element = document.querySelector("#" + elementId);
  element.parentNode.removeChild(element);
  populateHourTotals();
  // Decrement the TOTAL_FORMS
  const tf = parseInt(document.querySelector("#id_timecardobjects-TOTAL_FORMS").value);
  document.querySelector("#id_timecardobjects-TOTAL_FORMS").value = tf - 1;
  
}


// CONTRACT
// getParents :: element -> (array-of elements)
// PURPOSE
// Given an element, walk the DOM upwards until we hit 
// the top, returning everything found in an array.
function getParents(elem) {
  // Set up a parent array
  var parents = [];
  // Push each parent element to the array
  for (; elem && elem !== document; elem = elem.parentNode) {
    parents.push(elem);
  }
  // Return our parent array
  return parents;
}

// CONTRACT
// getParentsBySelector :: element string -> (array-of elements)
// PURPOSE
// Walks the tree upwards, keeping those parent elements that 
// match the given selector.
function getParentsBySelector(elem, selector) {
  // Element.matches() polyfill
  if (!Element.prototype.matches) {
    Element.prototype.matches =
      Element.prototype.matchesSelector ||
      Element.prototype.mozMatchesSelector ||
      Element.prototype.msMatchesSelector ||
      Element.prototype.oMatchesSelector ||
      Element.prototype.webkitMatchesSelector ||
      function (s) {
        var matches = (this.document || this.ownerDocument).querySelectorAll(s),
          i = matches.length;
        while (--i >= 0 && matches.item(i) !== this) {}
        return i > -1;
      };
  }
  // Set up a parent array
  var parents = [];
  // Push each parent element to the array
  for (; elem && elem !== document; elem = elem.parentNode) {
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
}
