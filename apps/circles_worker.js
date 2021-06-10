// Find all people connected directly to a specific person.
function get_neighbors(id, callback) {
  let xhr = new XMLHttpRequest();
  xhr.open("GET", "https://api.wikitree.com/api.php?action=getProfile&fields=Name,Id,Manager,Father,Mother,Parents,Children,Siblings,Spouses&key=" + id, /* async = */ true);  // TODO: Sanitize
  // Send credentials to allow loading private people.
  xhr.withCredentials = true;

  xhr.onload = function (e) {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {

        let result = JSON.parse(xhr.responseText);
        if (result[0]["status"] === 0) {
          result = result[0]["profile"];

          let neighbors = [];
          for (let relation of ["Parents", "Children", "Siblings", "Spouses"]) {
            for (let key in result[relation]) {
              let data = result[relation][key]
              neighbors.push({
                "id": data["Name"],
                "num": data["Id"],
                "is_user": (data["Id"] == data["Manager"]),
              });
            }
          }

          callback(neighbors);

        } else {  // result[0]["status"] != 0
          console.error("WikiTree API error loading id " + id);
          console.error(result[0]["status"]);
          console.error(result);
        }
      } else {  // xhr.status != 200
        console.error("HTTP error loading id " + id);
        console.error(xhr.statusText);
      }
    }
  };

  xhr.onerror = function (e) {
    console.error("XHR error loading id " + id);
    console.error(xhr.statusText);
  };

  xhr.send();
}

class Bfs {
  constructor(start) {
    this.start = start;
    this.visited = new Set();
    this.visited.add(start.id)
    this.todo = [start];
    this.circle_num = 0;
  }

  // Evaluating next circle. Calls callback when circle is complete.
  next_circle(callback) {
    // Note we create this alias self -> this to avoid JS interpretation
    // of this differently within callbacks!
    let self = this;
    self.circle_num += 1;
    let this_circle = [];
    let xhrs_waiting_for = self.todo.length;
    for (let person of self.todo) {
      get_neighbors(person.id, function(neighbors) {
        // console.log("neighbors of " + person + " : " + neighbors);
        for (let neigh of neighbors) {
          if (!self.visited.has(neigh.id)) {
            // Person not seen in previous circles.
            self.visited.add(neigh.id)
            this_circle.push(neigh)
          }
        }

        xhrs_waiting_for -= 1;
        if (xhrs_waiting_for == 0) {
          // All XHRs have finished.
          // Update object properties.
          self.todo = [...this_circle];
          // Call callback with all new people.
          callback({
            "circle_num": self.circle_num,
            "circle_nodes": this_circle,
            "cumulative_size": self.visited.size,
          });
        } else {
          // console.log("Bfs(" + self.circle_num + "): Waiting for " + xhrs_waiting_for + " more callbacks.");
        }
      })
    }
  }
}

function load_circles(focus_id, max_depth) {
  focus_node = {
    "id": focus_id,
  }
  let bfs = new Bfs(focus_node);

  function next_circle_callback(message) {
    postMessage(message)

    if (message.circle_num < max_depth) {
      bfs.next_circle(next_circle_callback);
    }
  }

  next_circle_callback({
    "circle_num": 0,
    "circle_nodes": [focus_node],
    "cumulative_size": 1,
  });
}

onmessage = function(e) {
  let message = e.data;
  console.log("Worker: Loading circles for " + message.focus_id + " " + message.depth);
  load_circles(message.focus_id, message.depth);
}
