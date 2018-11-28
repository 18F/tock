describe('Login', () => {
  it('should have path of "/" after login', () => {
    cy.login()

    cy.location().should((location) => {
      expect(location.origin).to.equal(Cypress.config('baseUrl'))
      expect(location.pathname).to.eq('/')
    })
  })
})

describe('Timecard', () => {
  before(cy.login)

  beforeEach(() => {
    Cypress.Cookies.preserveOnce('sessionid')
    cy.visit('/reporting_period/2015-03-30/')
  })

  it(`adds a project entry when 'Add Item' is clicked`, () => {
    cy.get('.entry').then($entries => {
      const length = $entries.length
      cy.get('.add-timecard-entry').click()
      cy.get('.entry').should('have.length', length + 1)
    })
  })

  it('sums the hours in each project entry and correctly rounds!', () => {
    // https://github.com/18F/tock/issues/848
    cy.get('#id_timecardobjects-0-hours_spent').type('.2')
    cy.get('.entries-total-reported-amount').should('have.text', '0.2')

    cy.get('.add-timecard-entry').click()
    cy.get('#id_timecardobjects-1-hours_spent').type('.2')
    cy.get('.entries-total-reported-amount').should('have.text', '0.4')

    cy.get('.add-timecard-entry').click()
    cy.get('#id_timecardobjects-2-hours_spent').type('.2')
    cy.get('.entries-total-reported-amount').should('have.text', '0.6')
  })

  // it('displays a line item for each line in the database', () => {
  // })
})
