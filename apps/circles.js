const e_form = document.querySelector("#input");
const e_focus = document.querySelector("#focus");
const e_depth = document.querySelector("#depth");
const e_result = document.querySelector("#result");

const worker = new Worker("circles_worker.js");

start_time = null;

e_form.addEventListener('submit', function(event) {
  // Avoid page reload: https://stackoverflow.com/questions/19454310/stop-form-refreshing-page-on-submit
  event.preventDefault();
  console.log("Form submission: " + e_focus.value + " " + e_depth.value);
  start_time = new Date();
  let focus = e_focus.value;
  let depth = e_depth.value;
  worker.postMessage({
    "focus": focus,
    "depth": depth,
  });
  e_result.textContent = "Exploring " + depth + " Circles around " + focus;
})

function post_result(connections) {
  let num_connections = connections.length;
  let distance = connections[0].length - 1;
  let start = connections[0][0];
  let end = connections[0][distance];

  // Write header info.
  let e_header = document.createElement("p");
  e_header.textContent = "Connections from " + start + " to " + end + ": Found " + num_connections + " connection of length " + distance;
  result.appendChild(e_header);
  // List of connections.
  let e_conns = document.createElement("ul");
  result.appendChild(e_conns);
  let i = 1;
  for (let connection of connections) {
    let e_conn_item = document.createElement("li");
    let e_conn_text = document.createElement("p");
    e_conn_text.textContent = "Connection " + i;
    e_conn_item.appendChild(e_conn_text);
    let e_conn = document.createElement("ol");
    e_conn_item.appendChild(e_conn);
    for (let person of connection) {
      let e_person = document.createElement("li");
      e_conn.appendChild(e_person);
      let e_person_link = document.createElement("a");
      e_person_link.href = "https://www.wikitree.com/wiki/" + person;
      e_person_link.textContent = person;
      e_person.appendChild(e_person_link)
    }
    // Attach to results.
    e_conns.appendChild(e_conn_item)
    i += 1;
  }
}

worker.onmessage = function(e) {
  let response = e.data;
  let time_diff = (new Date() - start_time) / 1000;

  let e_new = document.createElement("div");
  let e_summary = document.createElement("p");
  e_summary.textContent = "Circle " + response.circle_num + " / Size " + response.circle_ids.size + " / Cumulative " + response.cumulative_size + "  / " + time_diff + " seconds elapsed";
  e_new.appendChild(e_summary);

  circle_ids = Array.from(response.circle_ids);
  circle_ids.sort()
  console.log("Circle " + response.circle_num + " : " + circle_ids)
  // let e_list = document.createElement("ul");
  // for (let id of circle_ids) {
  //   let e_item = document.createElement("li");
  //   let e_person_link = document.createElement("a");
  //   e_person_link.href = "https://www.wikitree.com/wiki/" + id;
  //   e_person_link.textContent = id;
  //   e_item.appendChild(e_person_link);
  //   e_list.appendChild(e_item);
  // }
  // e_new.appendChild(e_list);

  e_result.appendChild(e_new);
}
