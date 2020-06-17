var baseURL = 'http://localhost:8000';

function login(username) {
    cy.visit('/');
    cy.get('#email')
        .type(`${username}{enter}`);
}

describe('basic interactions', () => {
    beforeEach(() => {
        login('malcolm.reynolds@gsa.gov');
        cy.get('h1').should('contain', 'Welcome to Tock');
        cy.window().then((win) => {
            ('clearLocalStorage');
        });
    });

    it('we made it to the landing page', () => {
        cy.get('h1').should('contain', 'Welcome to Tock');
    });

    it('test addition of new entries to form', () => {
        cy.visit('/reporting_period/2015-03-30/');
        cy.get('body > div.usa-content.usa-section > div > h1 > span').contains('March 30');
        
        cy.get('.entries').its('length').should('be', 1);
        cy.get('.add-timecard-entry').click();
        cy.get('.entries').its('length').should('be', 2);
    });
    
    it('add a project', () => {
        cy.visit('/reporting_period/2015-03-30/');
        cy.get('body > div.usa-content.usa-section > div > h1 > span').contains('March 30');
        // Set the hours to one.
        cy.get('#id_timecardobjects-0-hours_spent').type('1');
        // To select an element from the dropdown, we have to drive it indirectly.
        // The Chosen.js library gets in the way of interacting with the hidden, actual
        // select control. As a result, we need to select the <div> that Chosen.js inserts.
        // We do this by getting it via query, and then *typing* into the dropdown
        // the search we want to do.
        cy.get('#id_timecardobjects_0_project_chosen').type('109{enter}');
        cy.get('#id_timecardobjects-0-hours_spent').should('have.value', '1');
        // A new div is created by Chosen.js. This now will contain the text of the 
        // selected element. That should be a unique div, and we can check the 
        // contents of that div as if it were a static, text-containing div.
        cy.get('.chosen-single').should('contain', '109');
    });

});

describe('rounding tests', () => {
    beforeEach(() => {
        login('malcolm.reynolds@gsa.gov');
        cy.get('h1').should('contain', 'Welcome to Tock');
        cy.window().then((win) => {
            ('clearLocalStorage');
        });
    });

    it('sums the hours in each project entry and correctly rounds!', () => {
        // https://github.com/18F/tock/issues/848
        cy.visit('/reporting_period/2015-03-30/');
        cy.get('body > div.usa-content.usa-section > div > h1 > span').contains('March 30');
        cy.get('#id_timecardobjects-0-hours_spent').type('.2');
        cy.get('.entries-total-reported-amount').should('be', '.2');
        cy.get('.add-timecard-entry').click();
        cy.get('#id_timecardobjects-1-hours_spent').type('.2');
        cy.get('.entries-total-reported-amount').should('be', '.4');
        cy.get('.add-timecard-entry').click();
        cy.get('#id_timecardobjects-2-hours_spent').type('.2');
        cy.get('.entries-total-reported-amount').should('contain', '0');
      });
});

describe('exercising form elements', () => {
        beforeEach(() => {
            login('malcolm.reynolds@gsa.gov');
            cy.get('h1').should('contain', 'Welcome to Tock');
            cy.window().then((win) => {
                ('clearLocalStorage');
            });
        });
});