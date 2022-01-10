const baseUrl = process.env.TOCK_URL || `http://localhost:${process.env.JEST_PORT}`;

beforeAll(async () => {
  await page.goto(baseUrl);
  await page.type('input[name="email"]', "admin.user@gsa.gov");
  await page.keyboard.press("Enter");
  await page.waitForNavigation();
  await expect(page).toMatch("Tock your time");
}, 100000);

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

    test('added project entry has an unchecked delete input', async () => {
      const entries = await page.$$(".entry");
      const length = entries.length;
      // Find and check the last delete input on the page
      const last_entry_idx = length - 1
      const _del = "#id_timecardobjects-" + last_entry_idx + "-DELETE";
      await page.$$eval(_del, checks => checks.forEach(c => c.checked = true));

      // add new entry
      await page.click(".add-timecard-entry");

      // Is the newly added input checked? It shouldn't be
      const _new_delete_input = await page.$("#id_timecardobjects-" + length + "-DELETE");
      checked = await (await _new_delete_input.getProperty('checked')).jsonValue();
      expect(checked).toEqual(false);
    });

    test('checks if there is a checkbox image when image is checked', async () => {
      const entries = await page.$$(".entry");
      const length = entries.length;
      // Find and check the last delete input on the page
      const last_entry_idx = length - 1
      const _del = "#id_timecardobjects-" + last_entry_idx + "-DELETE";
      await page.$$eval(_del, checks => checks.forEach(c => c.checked = true));

      // add new entry
      await page.click(".add-timecard-entry");

      const _new_delete_input = await page.$("#id_timecardobjects-" + length + "-DELETE");
      await _new_delete_input.click;
      //need to get the right query selector - think this is rigth
      const background_image = await page.evaluate(() => {
        const checked_image = await(page.$$(`#id_timecardobjects-${length}-DELETE`));
        return window.getComputedStyle(checked_image).getPropertyValue("background-image");
      });
      expect(background_image).toMatch(/correct8.svg/);;
    });

    test('increments the django management form when "Add Item" is clicked', async () => {
      await page.click(".add-timecard-entry");
      const _entries = await page.$$(".entry");
      const totalforms = await page.evaluate(() => {
        return parseInt(document.querySelector("#id_timecardobjects-TOTAL_FORMS").value)
      })

      expect(_entries.length).toEqual(totalforms);
    });

    test("sums the hours in each project entry and correctly rounds!", async () => {
      // https://github.com/18F/tock/issues/848
      await page.evaluate(() => {
        document.querySelector("#id_timecardobjects-0-hours_spent").value = ''
      });
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
  });

  describe("handles weekly billing", () => {
    beforeEach(() => page.goto(`${baseUrl}/reporting_period/2015-03-30/`));

    test("hides hours input and shows project allocation element", async () => {
      // https://github.com/18F/tock/issues/848
      await page.evaluate(() => {
        document.querySelector("#id_timecardobjects-0-hours_spent").value = ''
      });

      // @TODO: Seed database with a weekly billing project and know the ID for this test
      await page.type(`#id_timecardobjects-0-project`, "125 - Weekly Billing Test");
      await page.keyboard.press("Enter");

      await page.waitForSelector(
        `.entry-project_allocation`, {
        visible: true,
        timeout: 5000
      });

      // We should now be in a state where the hour input is hidden and the project allocation dropdown is available
      const _allocationPercentageClassListObj = await page.$eval(".entry-project_allocation", el => el.classList);
      const _allocationPercentageClassList = Array.from(Object.values(_allocationPercentageClassListObj));
      const allocationPercentageVisible = !_allocationPercentageClassList.includes('entry-hidden');

      const _hourlyClassListObj = await page.$eval(".entry-hours_spent", el => el.classList);
      const _hourlyClassList = Array.from(Object.values(_hourlyClassListObj));
      const hourlyInputHidden = _hourlyClassList.includes('entry-hidden');

      expect(allocationPercentageVisible).toBe(true);
      expect(hourlyInputHidden).toBe(true);
    });

    test("hides hour summation elements once a weekly billing project is added", async () => {
      // https://github.com/18F/tock/issues/848
      await page.evaluate(() => {
        document.querySelector("#id_timecardobjects-0-hours_spent").value = ''
      });

      let _totalReportedElement = await page.$eval("#total-reported-div", el => el.classList);
      let _totalReportedClassList = Array.from(Object.values(_totalReportedElement));

      let _totalBillableElement = await page.$eval("#total-billable-div", el => el.classList);
      let _totalBillableClassList = Array.from(Object.values(_totalBillableElement));

      let _totalReportedVisible = !_totalReportedClassList.includes('entry-hidden');
      let _totalBillableVisible = !_totalBillableClassList.includes('entry-hidden');
      const bothSummationElementsVisible = _totalReportedVisible && _totalBillableVisible;

      expect(bothSummationElementsVisible).toBe(true);
      
      await page.type(`#id_timecardobjects-0-project`, "125 - Weekly Billing Test");
      await page.keyboard.press("Enter");

      await page.waitForSelector(
        `.entry-project_allocation`, {
        visible: true,
        timeout: 5000
      });

      _totalReportedElement = await page.$eval("#total-reported-div", el => el.classList);
      _totalReportedClassList = Array.from(Object.values(_totalReportedElement));

      _totalBillableElement = await page.$eval("#total-billable-div", el => el.classList);
      _totalBillableClassList = Array.from(Object.values(_totalBillableElement));

      const _totalReportedHidden = _totalReportedClassList.includes("entry-hidden");
      const _totalBillableHidden = _totalBillableClassList.includes("entry-hidden");
      const bothSummationElementsHidden = _totalReportedHidden && _totalBillableHidden;

      expect(bothSummationElementsHidden).toBe(true);

      const _weeklyBillingAlertElement = await page.$eval("#weekly-billing-alert", el => el.classList);
      const _weeklyBillingAlertClassList = Array.from(Object.values(_weeklyBillingAlertElement));
      const weeklyBillingAlertVisible = !_weeklyBillingAlertClassList.includes("entry-hidden");

      expect(weeklyBillingAlertVisible).toBe(true);
    });
  });

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
