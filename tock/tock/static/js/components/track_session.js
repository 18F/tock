(function trackSessions() {
  function extendSession() {
    var request = new XMLHttpRequest();
    request.open('GET', '/session-extend', true);
    request.send()
  }

  function logout() {
    window.location.reload()
  }

  function ping() {
    var request = new XMLHttpRequest();
    request.open('GET', '/session-warning', true);

    request.onload = function() {
      if (request.status === 401) {
        alert("Your session has expired. Please log back in.")
        logout()
      }
      if (request.status >= 200 && request.status < 400) {
        if (JSON.parse(request.responseText)["warn_about_expiration"]) {
          let extend = confirm("Your session is about to expire! Would you like to extend the session?")
          if (extend) {
            extendSession()
          } else {
            return
          }
        }
      }
    };

    request.send();
    setTimeout(ping, 20 * 1000)
  }
  ping()
})(window);