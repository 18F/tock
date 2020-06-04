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


    // FIXME MCJ 20200604
    // It would be nice if we were consistent with - and _ in naming.
    await page.screenshot({"path" : "t1.png"});

    await page.select("#id_timecardobjects-0-project", "109");
    await page.click("#id_timecardobjects-0-hours_spent", {clickCount: 3})
    await page.type("#id_timecardobjects-0-hours_spent", "1");
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
    await page.screenshot({ path: "t1.png" });
    await page.select("#id_timecardobjects-0-project", "109");
    await page.click("#id_timecardobjects-0-hours_spent", {clickCount: 3})
    await page.type("#id_timecardobjects-0-hours_spent", "1");
    await page.screenshot({"path" : "t2.png"});
    
    await page.click('.add-timecard-entry');
    
    await page.screenshot({"path" : "t3.png"});

    await page.select("#id_timecardobjects-1-project", "29");
    await page.click("#id_timecardobjects-1-hours_spent", {clickCount: 3})
    await page.type("#id_timecardobjects-1-hours_spent", "8");

    // Next, mark the first entry for deletion.
    // await page.click("#id_timecardobjects-0-DELETE");

    var resultArray = null;
    resultArray = await page.evaluate( () => { 
      return getFormData();
    });

    // Expect at leaset one entry to have hours == 1
    expect(resultArray.map( (e) => { return e.hours } )).toEqual(expect.arrayContaining([8, 1]));
    expect(resultArray.map( (e) => { return e.project } )).toEqual(expect.arrayContaining([29, 109]));
  });

});

