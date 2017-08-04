(function setup_notifications() {
  if("Notification" in window) {
    Notification.requestPermission().then(function(result) {
      // If the user grants permission, or has granted permission in the past,
      // setup the timers.  Otherwise bail out.
      if (result !== 'granted') {
        return;
      }

      var setTimer = function() {
        var now = new Date();
        var target;

        // If it's Friday and before 3pm... (local times)
        if(now.getDay() == 5 && now.getHours() < 15) {
          // ...target is later today
          var hoursForward = 15 - now.getHours();
          target = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() + hoursForward);
        } else {
          // ...target is forward to the next Friday
          var daysForward = 5 - now.getDay();
          if(daysForward < 1) {
            daysForward += 7;
          }

          target = new Date(now.getFullYear(), now.getMonth(), now.getDate() + daysForward, 15);
        }

        // Now compute the time difference between now and
        // the target, so we know when to send up the notification.
        var delay = target.getTime() - now.getTime();
        setTimeout(issueNotification, delay);
      };

      var issueNotification = function() {
        new Notification('Tock Your Time!', {
          body: 'Don\'t forget to Tock your time before COB!',
          requireInteraction: true,
          icon: '/static/img/favicon.ico'
        });

        // Setup the next notification, but wait a few seconds to
        // make sure the hour has rolled over.
        setTimeout(setTimer, 10000);
      };

      setTimer();
    });
  }
})();
