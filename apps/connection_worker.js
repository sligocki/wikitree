

// Find all people connected directly to a specific person.
function getNeighbors(id, callback) {
  let xhr = new XMLHttpRequest();
  xhr.open("GET", "https://api.wikitree.com/api.php?action=getProfile&fields=Name,Father,Mother,Parents,Children,Siblings,Spouses&key=" + id, /* async = */ true);  // TODO: Sanitize

  xhr.onload = function (e) {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {

        let result = JSON.parse(xhr.responseText);
        result = result[0]["profile"];

        let neighbors = [];
        for (let key in result["Parents"]) {
          neighbors.push(result["Parents"][key]["Name"]);
        }
        for (let key in result["Children"]) {
          neighbors.push(result["Children"][key]["Name"]);
        }
        for (let key in result["Siblings"]) {
          neighbors.push(result["Siblings"][key]["Name"]);
        }
        for (let key in result["Spouses"]) {
          neighbors.push(result["Spouses"][key]["Name"]);
        }

        callback(neighbors);

      } else {
        console.error(xhr.statusText);
      }
    }
  };

  xhr.onerror = function (e) {
    console.error(xhr.statusText);
  };

  xhr.send();
}

class Bfs {
  constructor(start) {
    this.start = start;
    this.paths = new Map();
    this.paths.set(start, []);
    this.todo = [start];
    this.num_steps = 0;
  }

  // Calculate next generation and call callback when all responses come back.
  next_gen(callback) {
    let self = this;
    self.num_steps += 1;
    let new_paths = new Map();
    let xhrs_waiting_for = self.todo.length;
    for (let person of self.todo) {
      getNeighbors(person, function(neighbors) {
        for (let neigh of neighbors) {
          if (!self.paths.has(neigh)) {
            // Person not seen in previous generations.
            if (!new_paths.has(neigh)) {
              new_paths.set(neigh, []);
            }
            new_paths.get(neigh).push(person);
          }
        }

        xhrs_waiting_for -= 1;
        if (xhrs_waiting_for == 0) {
          // All XHRs have finished.
          // Update object properties.
          self.todo = [...new_paths.keys()];
          self.paths = new Map([...new_paths, ...self.paths]);
          // Call callback with all new people.
          callback(self.todo);
        } else {
          // console.log("Bfs(" + self.num_steps + "): Waiting for " + xhrs_waiting_for + " more callbacks.");
        }
      })
    }
  }

  // Get a path from this.start -> person (not including person).
  get_out_paths(person) {
    let paths = [];
    if (person == this.start) {
      // One path, length 0.
      paths.push([]);
    } else {
      for (var next of this.paths.get(person)) {
        for (var subpath of this.get_out_paths(next)) {
          paths.push([...subpath, next]);
        }
      }
    }
    return paths;
  }

  get_in_paths(person) {
    let paths = this.get_out_paths(person);
    for (let path of paths) {
      path.reverse();
    }
    return paths;
  }
}

function getConnection(person1, person2, start_time, callback) {
  let bfs1 = new Bfs(person1);
  let bfs2 = new Bfs(person2);

  function step() {
    let time_diff = (new Date() - start_time) / 1000;
    console.log("Worker: Evaluated " + bfs1.paths.size + " (" + bfs1.num_steps + " around " + person1 + ") & " + bfs2.paths.size + " (" + bfs2.num_steps + " around " + person2 + ") in " + time_diff + "s");
    postMessage({
      "done": false,
      "num_steps": bfs1.num_steps + bfs2.num_steps,
      "num_people": bfs1.paths.size + bfs2.paths.size,
    })

    // See if we have found a connection yet.
    let connections = [];
    for (let person of bfs1.todo) {
      if (bfs2.paths.has(person)) {
        for (let path1 of bfs1.get_out_paths(person)) {
          for (let path2 of bfs2.get_in_paths(person)) {
            connections.push([...path1, person, ...path2]);
          }
        }
      }
    }
    if (connections.length > 0) {
      callback(connections);
      return;
    }

    // If we're not done yet, expand the smaller todo list one more level.
    // TODO: step both at once?
    if (bfs1.todo.length <= bfs2.todo.length) {
      bfs1.next_gen(step);
    } else {
      bfs2.next_gen(step);
    }
  }

  step();
}

onmessage = function(e) {
  let start_time = new Date();
  console.log("Worker: Recieved message " + e.data);
  let person1 = e.data[0];
  let person2 = e.data[1];

  getConnection(person1, person2, start_time, function(connections) {
    let time_diff = (new Date() - start_time) / 1000;
    console.log("Worker: found result in time: " + time_diff + "s")
    postMessage({
      "done": true,
      "result": connections,
    });
  });
}
