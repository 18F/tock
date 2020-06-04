const baseUrl = `http://localhost:${process.env.JEST_PORT}`;

// First, create a billing period.
// If not, none of the tests will work.
beforeAll(async () => {
  await page.goto(baseUrl);
  await page.type('input[name="email"]','malcolm.reynolds@gsa.gov');
  await page.keyboard.press('Enter');
  await page.waitForNavigation();
  await expect(page).toMatch('Welcome to Tock!');
  /*
  // Go to the create page.
  await page.goto(`${baseUrl}/reporting_period/create`);
  // Insert the start/end dates
  await page.type("#id_start_date", "05/25/2020");
  await page.type("#id_end_date", "05/29/2020");
  // Select based on the type attribute.
  await page.click("[type='submit']");
  // Wait for 3 seconds.
  await page.waitFor(3000);
  if (page.$("Welcome to Tock")) {
    await page.screenshot({path : "didnotexist.png"});
  } else {
    await page.screenshot({path : "didexist.png"});
  }
  */
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
    // FIXME MCJ 20200604
    // It would be nice if we were consistent with - and _ in naming.
    await page.select("#id_timecardobjects-0-project", "109");
    await page.type("#id_timecardobjects-0-hours_spent", "1");
    // Add it, so it is part of the page.
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

  /*
  test('sums the hours in each project entry and correctly rounds!', async () => {
    // https://github.com/18F/tock/issues/848
    await page.type('#id_timecardobjects-0-hours_spent', '.2');
    await expect(page).toMatchElement('.entries-total-reported-amount', { text: '0.2' });

    await page.click('.add-timecard-entry');
    await page.type('#id_timecardobjects-1-hours_spent', '.2');
    await expect(page).toMatchElement('.entries-total-reported-amount', { text: '0.4'});

    await page.click('.add-timecard-entry');
    await page.type('#id_timecardobjects-2-hours_spent', '.2');
    await expect(page).toMatchElement('.entries-total-reported-amount', { text: '0.6'});
  });
  */
});

