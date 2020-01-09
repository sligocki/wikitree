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

function unrollChain(paths, start, end) {
  var chain = [start];
  var person = start;
  var i = 0;
  while (person != end) {
    person = paths[person][0];  // TODO: Allow multiple connections.
    chain.push(person);
    i += 1;
  }
  return chain;
}

function getConnection(person1, person2) {
  var gen = [person1];
  // Dict { person : [list of neighbors of person on shortest paths to person1] }
  var paths = {person1: []};

  var num_lookups = 0;
  while (Object.keys(paths).length < 1000) {
    var new_gen = [];
    for (var i = 0; i < gen.length; ++i) {
      person = gen[i];
      neighbors = getNeighborsBlocking(person);
      num_lookups += 1;
      for (var j = 0; j < neighbors.length; ++j) {
        neighbor = neighbors[j];
        if (!(neighbor in paths)) {
          paths[neighbor] = [];
          new_gen.push(neighbor);
        }
        paths[neighbor].push(person)
        if (neighbor == person2) {  // TODO: allow bidirectional.
          console.log("Searched " + num_lookups + " people.")
          return unrollChain(paths, person2, person1);
        }
      }
    }
    gen = new_gen;
  }

  return "No connection found."
}

onmessage = function(e) {
  var startTime = new Date();
  console.log("Worker: Recieved message " + e.data);
  var start = e.data[0];
  var end = e.data[1];

  var result = getConnection(start, end);

  var timeDiff = (new Date() - startTime) / 1000;
  console.log("Worker: Posting response " + result + " (Time: " + timeDiff + "s)");
  postMessage(result);
}
