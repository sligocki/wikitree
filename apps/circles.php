<html>
  <head>
    <title>Circle Explorer</title>

    <!-- For convenience, use JQuery for our Ajax interactions with the API. Use the cookie module to grab any existing user id. -->
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
    <script src="/apps/jquery.cookie.js"></script>

    <!-- Use the WikiTree JavaScript SDK beta to hold our session and wrap our calls to the API URL. -->
    <script src="/apps/wikitree.js"></script>

    <script type="text/javascript">
      // When the DOM is ready, check to see if the user is already logged in. If so we'll note this in the page.
      $(document).ready(function(){
      	wikitree.init({});

      	// checkLogin calls the API URL with action=login and user_id = (stored user_id).
      	// The API returns the user id if the user is signed in.
      	// Use the logged-in status to show/hide some content on the page.
      	wikitree.session.checkLogin({})
      		.then(function(data) {
      			if (wikitree.session.loggedIn) {
      				/* We're already logged in and have a valid session. */
      				$('.logged_out').hide();
      				$('.logged_in').show();
      				$('#user_name_label').html(wikitree.session.user_name);
      				$('#user_id_label').html(wikitree.session.user_id);
      			}
      			else {
      				// The checkLogin failed, so the user isn't already logged in (doesn't have a session cookie at api.wikitree.com).
      				// Our application URL here might have been returned to by a clientLogin attempt, however.
      				// See if we have an authorization code we can use to complete the login.

      				var x = window.location.href.split('?');
      				var queryParams = new URLSearchParams( x[1] );
      				if (queryParams.has('authcode')) {
      					// We have an authcode. Send that to the API's "clientLogin" action to see if it's valid.
      					// On success, the wikitree.js clientLogin function will set "loggedIn" to true and store the user_id and user_name.
      					var authcode = queryParams.get('authcode');
      					wikitree.session.clientLogin( {'authcode': authcode}  )
      						.then(function(data) {
      							if (wikitree.session.loggedIn) {
      								// If we're logged in, let's redirect back to ourselves just to clean out the authcode from
      								// the URL. We don't want user's to bookmark that since it's temporary.
      								window.location = 'api_demo_new.php';
      							}
      							else {
      								// Our clientLogin action failed. So the user is not in fact logged in.
      								$('.logged_out').show();
      								$('.logged_in').hide();
      							}
      						});
      				} else {
      					// We don't have an authorization code to try, so the user is just not logged in.
      					$('.logged_out').show();
      					$('.logged_in').hide();
      				}
      			}
      		});
      });
    </script>
  </head>

  <body>
    <div class="logged_out">
      <form action="https://api.wikitree.com/api.php" method="POST">
    		<input type="hidden" name="action" value="clientLogin"/>
    		<input type="hidden" name="returnURL" value="https://apps.wikitree.com/apps/ligocki7/circles.php"/>
    		<input type="submit" value="Client Login"/>
  		</form>
    </div>
    <div class="logged_in">
      You are logged in.
    </div>
    <hr/>

    <form id="input">
      <div>
        <label for="focus">Focus id: </label>
        <input type="text" id="focus" value="Ligocki-7"/>
        <label for="depth">Number of circles: </label>
        <input type="text" id="depth" value="6"/>
      </div>
      <input type="submit"/>
    </form>
    <hr/>

    <div id="result">None</div>

    <script src="circles.js"></script>
  </body>
</html>
