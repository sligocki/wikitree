<html>
  <head>
    <title>Nearest Genealogists</title>
  </head>

  <body>
    <form id="input">
      <div>
        <label for="start">Start id: </label>
        <input type="text" id="start" value="Ligocki-7">
      </div>
      <input type="submit">
    </form>

    <p>Number of profiles searched: <div id="num_profiles_searched">0</div></p>
    <p>Searching at distance: <div id="search_distance">0</div></p>
    <p>Status: <div id="status">No search started yet</div></p>
    <ul id="result_list">
    </ul>

    <script src="nearest_genealogists.js"></script>
  </body>
</html>
