// Find all people connected directly to a specific person.
function get_neighbors(id, callback) {
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
    this.visited = new Set();
    this.visited.add(start)
    this.todo = [start];
    this.circle_num = 0;
  }

  // Evaluating next circle. Calls callback when circle is complete.
  next_circle(callback) {
    // Note we create this alias self -> this to avoid JS interpretation
    // of this differently within callbacks!
    let self = this;
    self.circle_num += 1;
    let this_circle = new Set();
    let xhrs_waiting_for = self.todo.length;
    for (let person of self.todo) {
      get_neighbors(person, function(neighbors) {
        // console.log("neighbors of " + person + " : " + neighbors);
        for (let neigh of neighbors) {
          if (!self.visited.has(neigh)) {
            // Person not seen in previous circles.
            this_circle.add(neigh)
          }
        }

        xhrs_waiting_for -= 1;
        if (xhrs_waiting_for == 0) {
          // All XHRs have finished.
          // Update object properties.
          self.todo = [...this_circle];
          self.visited = new Set([...self.visited, ...this_circle])
          // Call callback with all new people.
          callback({
            "circle_num": self.circle_num,
            "circle_ids": this_circle,
            "cumulative_size": self.visited.size,
          });
        } else {
          // console.log("Bfs(" + self.circle_num + "): Waiting for " + xhrs_waiting_for + " more callbacks.");
        }
      })
    }
  }
}

function load_circles(focus, max_depth) {
  let bfs = new Bfs(focus);

  function next_circle_callback(message) {
    postMessage(message)

    if (message.circle_num < max_depth) {
      bfs.next_circle(next_circle_callback);
    }
  }

  next_circle_callback({
    "circle_num": 0,
    "circle_ids": new Set([focus]),
    "cumulative_size": 1,
  });
}

onmessage = function(e) {
  let message = e.data;
  console.log("Worker: Loading circles for " + message.focus + " " + message.depth);
  load_circles(message.focus, message.depth);
}
