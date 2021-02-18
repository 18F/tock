const baseUrl = `http://localhost:${process.env.JEST_PORT}`;

beforeAll(async () => {
  await page.goto(baseUrl);
  await page.type('input[name="email"]', "admin.user@gsa.gov");
  await page.keyboard.press("Enter");
  await page.waitForNavigation();
  await expect(page).toMatch("Tock your time");
});

beforeEach(async () => page.goto(baseUrl));

describe("Login", () => {
  test('should have path of "/" after login', async () => {
    await expect(page.url()).toEqual(baseUrl + "/");
    await expect(page).toMatch("Tock your time");
  });
});

describe("Timecard", () => {
  describe("no setup needed", () => {
    beforeEach(() => page.goto(`${baseUrl}/reporting_period/2015-03-30/`));

    test('adds a project entry when "Add Item" is clicked', async () => {
      const entries = await page.$$(".entry");
      const length = entries.length;
      await page.click(".add-timecard-entry");
      const _entries = await page.$$(".entry");
      expect(_entries.length).toEqual(length + 1);
    });

    test("sums the hours in each project entry and correctly rounds!", async () => {
      // https://github.com/18F/tock/issues/848
      await page.evaluate(() => {
        document.querySelector("#id_timecardobjects-0-hours_spent").value = ''
      })
      await page.type("#id_timecardobjects-0-hours_spent", ".2");
      await page.keyboard.press("Enter")
      await expect(page).toMatchElement(".entries-total-reported-amount", {
        text: "0.2",
      });

      await page.click(".add-timecard-entry");
      await page.type("#id_timecardobjects-1-hours_spent", ".2");
      await page.keyboard.press("Enter")
      await expect(page).toMatchElement(".entries-total-reported-amount", {
        text: "0.4",
      });
  
      await page.click(".add-timecard-entry");
      await page.type("#id_timecardobjects-2-hours_spent", ".2");
      await page.keyboard.press("Enter")
      await expect(page).toMatchElement(".entries-total-reported-amount", {
        text: "0.6",
      });
    });
  })
 
  describe("notes", () => {
    beforeEach(() => {
      jest.setTimeout(20000);
    })

    xdescribe("tocklines that are prepopulated", () => {
      describe("that requires notes", () => {
        // TODO: figure out how to seed specific test data
        beforeEach(() => {
          return page.goto(`${baseUrl}/reporting_period/2015-03-30/`);
        })

        test("the notes are visible", async () => {
          const id = 0
          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: true 
          });
        });
      });

      describe("that do not require notes", () => {
        // TODO: figure out how to seed specific test data
        beforeEach(() => {
          return page.goto(`${baseUrl}/reporting_period/2015-03-30/`);
        })

        test("the notes are not visible", async () => {
          const id = 0
          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: false 
          });
        });
      });
    });

    describe("tocklines added from add-timecard-entry", () => {
      beforeEach(() => page.goto(`${baseUrl}/reporting_period/2015-03-30/`));
      describe("that requires notes", () => {
        test("notes are visible on the page", async () => {
          await page.$$(".entry");
          await page.click(".add-timecard-entry");
          const entries = await page.$$(".entry");
          const id = entries.length - 1

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: false 
          });

          await page.type(`#id_timecardobjects-${id}-project`, "124 - notes Project")
          await page.type(`#id_timecardobjects-${id}-hours_spent`, ".2")

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: true 
          });
        })
      })

      describe("that does not require notes", () => {
        test("notes are note visible on the page", async () => {
          await page.$$(".entry");
          await page.click(".add-timecard-entry");
          const entries = await page.$$(".entry");
          const id = entries.length - 1

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: false 
          });

          await page.type(`#id_timecardobjects-${id}-project`, "7nlE6t Project")
          await page.type(`#id_timecardobjects-${id}-hours_spent`, ".2")

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: false 
          });
        })
      })
    })

    describe("updating an existing tock line", () => {
      beforeEach(() => page.goto(`${baseUrl}/reporting_period/2015-03-30/`));
      describe("that requires notes", () => {
        test("notes are visible on the page", async () => {
          const entries = await page.$$(".entry");
          const id = entries.length - 1

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: false 
          });

          await page.type(`#id_timecardobjects-${id}-project`, "124 - notes Project")
          await page.type(`#id_timecardobjects-${id}-hours_spent`, ".2")

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: true 
          });
        })
      })

      describe("that does not require notes", () => {
        test("notes are note visible on the page", async () => {
          const entries = await page.$$(".entry");
          const id = entries.length - 1

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: false 
          });

          await page.type(`#id_timecardobjects-${id}-project`, "7nlE6t Project")
          await page.type(`#id_timecardobjects-${id}-hours_spent`, ".2")

          await page.waitForSelector(
            `#id_timecardobjects-${id}-notes`, {
            visible: false 
          });
        })
      })
    })
  });
});