const baseUrl = `http://localhost:${process.env.JEST_PORT}`;

beforeAll(async () => {
  await page.goto(baseUrl);
  await page.type('input[name="email"]','admin.user@gsa.gov');
  await page.keyboard.press('Enter');
  await page.waitForNavigation();
  await expect(page).toMatch('Welcome to Tock!');
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

  test('adds a project entry when "Add Item" is clicked', async () => {
    const entries = await page.$$('.entry');
    const length = entries.length;
    await page.click('.add-timecard-entry');
    const _entries = await page.$$('.entry');
    await expect(_entries.length).toEqual(length + 1);
  });

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
});
