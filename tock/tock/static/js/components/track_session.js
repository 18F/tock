(function trackSessions() {
  function extendSession() {
    var request = new XMLHttpRequest();
    request.open("GET", "/session-extend", true);
    request.onload = function () {
      if (request.status === 401) {
        alert("Your session has expired. Please log back in.");
        logout();
      }
    };
    request.send();
  }

  function logout() {
    window.location.reload();
  }

  const timeoutCount = document.querySelector("body").dataset.timeoutCount;

  function setAlert() {
    alert(
      "Your session is about to expire! We will attempt to refresh your session."
    );
    extendSession();
  }

  setTimeout(setAlert, timeoutCount - 120 * 1000);
})(window);
