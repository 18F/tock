const baseUrl = `http://localhost:${process.env.JEST_PORT}`;

// First, create a billing period.
// If not, none of the tests will work.
beforeAll(async () => {
  await page.goto(baseUrl);
  await page.type('#email', 'malcolm.reynolds@gsa.gov');
  await page.keyboard.press('Enter');
  await page.waitForNavigation();
  await expect(page).toMatch('Welcome to Tock!');

  // Lets see more in screenshots.
  await page.setViewport({ width: 1920, height: 2160 });
});

afterAll(async () => {
  await page.goto(`${baseUrl}/logout`);
});

beforeEach(async () => page.goto(baseUrl));

describe('Login', () => {
  test('should have path of "/" after login', async () => {
    await expect(page.url()).toEqual(baseUrl + '/');
    await expect(page).toMatch('Welcome to Tock!');
  });
});

describe('Timecard', () => {
  beforeEach(() => page.goto(`${baseUrl}/reporting_period/2015-03-30/`));

  test('add a 1 hour item to project 109', async () => {
    await page.evaluate( () => { 
      return clearLocalStorage();
    });

    await page.screenshot({'path' : 't1.png'});

    await page.select('#id_timecardobjects-0-project', '109');
    await page.click('#id_timecardobjects-0-hours_spent', {clickCount: 3})
    await page.type('#id_timecardobjects-0-hours_spent', '1');
    // Add a new entry, for the next action
    await page.click('.add-timecard-entry');
    // Now, call getFormData, and see if we get one element in the array.
    var resultArray = null;
    resultArray = await page.evaluate( () => { 
      return getFormData();
    });

    // Expect at leaset one entry to have hours == 1
    expect(resultArray.map( (e) => { return e.hours } )).toEqual(expect.arrayContaining([1]));
    expect(resultArray.map( (e) => { return e.project } )).toEqual(expect.arrayContaining([109]));
  });

  
  test('add two elements', async () => {
    await page.evaluate( () => { 
      return clearLocalStorage();
    });
  
    var entries = [ {'project': '109', 'hours': '1'},
                    {'project': '29', 'hours': '8'},
                  ];

    for (var ndx = 0; ndx < entries.length ; ndx++) {
      obj = entries[ndx];
      await page.select(`#id_timecardobjects-${ndx}-project`, obj.project);
      await page.click(`#id_timecardobjects-${ndx}-hours_spent`, {clickCount: 3})
      await page.type(`#id_timecardobjects-${ndx}-hours_spent`, obj.hours);
      await page.click('.add-timecard-entry');  
    }

    var resultArray = null;
    resultArray = await page.evaluate( () => { 
      return getFormData();
    });

    // Expect at leaset one entry to have hours == 1
    expect(resultArray.map( (e) => { return e.hours } )).toEqual(expect.arrayContaining([8, 1]));
    expect(resultArray.map( (e) => { return e.project } )).toEqual(expect.arrayContaining([29, 109]));
  }); // end test

  test('add two elements, delete one', async () => {
    await page.evaluate( () => { 
      return clearLocalStorage();
    });

    var entries = [ {'project': '109', 'hours': '1'},
                    {'project': '29', 'hours': '8'}
                  ];

    for (var ndx = 0; ndx < entries.length ; ndx++) {
      obj = entries[ndx];
      await page.select(`#id_timecardobjects-${ndx}-project`, obj.project);
      await page.click(`#id_timecardobjects-${ndx}-hours_spent`, {clickCount: 3})
      await page.type(`#id_timecardobjects-${ndx}-hours_spent`, obj.hours);
      await page.click('.add-timecard-entry');  
    }

    // Next, mark the first entry for deletion.
    await page.click('label[for="id_timecardobjects-0-DELETE"]');

    var resultArray = null;
    resultArray = await page.evaluate( () => { 
      return getFormData();
    });

    expect(resultArray.map( (e) => { return e.hours } )).toEqual(expect.arrayContaining([8]));
    expect(resultArray.map( (e) => { return e.project } )).toEqual(expect.arrayContaining([29]));
    expect(resultArray.map( (e) => { return e.hours } )).toEqual(expect.not.arrayContaining([1]));
    expect(resultArray.map( (e) => { return e.project } )).toEqual(expect.not.arrayContaining([109]));
  }); // end test

  test('test the getHoursReport function', async () => {
    // This calls getFormData() internally. It then builds
    // an object that contains information used to build the 
    // spinny displays at the bottom of the page.

    // // Round user input to .01; round system to .5
    // return {
    //   totalHours: round(r.totalHours),
    //   excludedHours: round(r.excludedHours),
    //   nonBillableHours: round(r.totalHours - r.billableHours - r.excludedHours),
    //   billableHours: round(r.billableHours),
    //   billableHoursTarget: roundToNearestHalf((totalHoursTarget - r.excludedHours) * billableExpectation),
    // };

    await page.evaluate( () => { 
      return clearLocalStorage();
    });

    var entries = [ {'project': '109', 'hours': '1.5'},
                    {'project': '29', 'hours': '8'},
                    {'project': '113', 'hours': '1.01'}
                  ];

    for (var ndx = 0; ndx < entries.length ; ndx++) {
      obj = entries[ndx];
      await page.select(`#id_timecardobjects-${ndx}-project`, obj.project);
      await page.click(`#id_timecardobjects-${ndx}-hours_spent`, {clickCount: 3})
      await page.type(`#id_timecardobjects-${ndx}-hours_spent`, obj.hours);
      await page.click('.add-timecard-entry');  
    }

    // I should have 1.5 + 8 + 1.01 hours, or 10.51 hours.
    var result = null;
    result = await page.evaluate( () => { 
      return getHoursReport();
    });

    expect(result.totalHours).toBe(10.51);
  }); // end test


  test('test localStorage after populateHourTotals', async () => {
    await page.evaluate( () => { 
      return clearLocalStorage();
    });

    var entries = [ {'project': '109', 'hours': '1.5'},
                    {'project': '29', 'hours': '8'},
                    {'project': '113', 'hours': '1.01'}
                  ];

    for (var ndx = 0; ndx < entries.length ; ndx++) {
      obj = entries[ndx];
      await page.select(`#id_timecardobjects-${ndx}-project`, obj.project);
      await page.click(`#id_timecardobjects-${ndx}-hours_spent`, {clickCount: 3})
      await page.type(`#id_timecardobjects-${ndx}-hours_spent`, obj.hours);
      await page.click('.add-timecard-entry');  
    }

    // objectId is a magic variable set in the Jinja template for 
    // the timecard page. It should be in scope when the page.evaluate()
    // is executed. ¯\_(ツ)_/¯
    // I don't like it, but this is the joy of front-end testing.
    const result = await page.evaluate( () => {
      populateHourTotals();
      hoursAsEntered = window.localStorage.getItem(`tock-entered-hours-${objectId}`);
      // hoursAsEntered should be a stringified array of objects, each object having a
      // 'project' and 'hours' field. So, exactly like what was added above.
      return JSON.parse(hoursAsEntered);
    });
    var hoursArray = result.map( e => { return e.hours });
    var projectArray = result.map ( e => { return e.project });

    for (obj of entries) {
      expect(hoursArray).toEqual(expect.arrayContaining([obj.hours]));
      expect(projectArray).toEqual(expect.arrayContaining([obj.project]));
    }
  }); // end test

});

