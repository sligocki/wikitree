<html>
  <head>
    <title>Connection Finder</title>
  </head>
  <body>
    <script>
// Find all people connected directly to a specific person.
// Blocking / synchronous call.
function getNeighborsBlocking(id) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/api.php?action=getProfile&fields=Name,Father,Mother,Parents,Children,Siblings,Spouses&key=" + id, /* async = */ false);  // TODO: Sanitize
  xhr.send();

  var result = JSON.parse(xhr.responseText);
  result = result[0]["profile"];

  var neighbors = [];
  for (var key in result["Parents"]) {
    neighbors.push(result["Parents"][key]["Name"]);
  }
  for (var key in result["Children"]) {
    neighbors.push(result["Children"][key]["Name"]);
  }
  for (var key in result["Siblings"]) {
    neighbors.push(result["Siblings"][key]["Name"]);
  }
  for (var key in result["Spouses"]) {
    neighbors.push(result["Spouses"][key]["Name"]);
  }

  return neighbors;
}

function unrollChain(paths, person) {
  chain = [person];
  while (paths[person]) {
    person = paths[person][0];  // TODO: Allow multiple connections.
    chain.push(person);
  }
  return chain;
}

function getConnection(person1, person2) {
  var gen = [person1];
  // Dict { person : [list of neighbors of person on shortest paths to person1] }
  var paths = {person1: []};

  while (Object.keys(paths).length < 1000) {
    var new_gen = [];
    for (var i = 0; i < gen.length; ++i) {
      person = gen[i];
      neighbors = getNeighborsBlocking(person);
      for (var j = 0; j < neighbors.length; ++j) {
        neighbor = neighbors[j];
        if (!(neighbor in paths)) {
          paths[neighbor] = [];
          new_gen.push(neighbor);
        }
        paths[neighbor].push(person)
        if (neighbor == person2) {  // TODO: allow bidirectional.
          return unrollChain(paths, person2);
        }
      }
    }
    gen = new_gen;
  }

  // No connection.
}

var person1 = "Ligocki-7";
var person2 = "Ligocki-9";

//alert(getConnection(person1, person2));
    </script>
  </body>
</html>
