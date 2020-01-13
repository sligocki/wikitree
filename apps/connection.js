const e_form = document.querySelector("#input");
const e_start = document.querySelector("#start");
const e_end = document.querySelector("#end");
const e_result = document.querySelector("#result");

const worker = new Worker("connection_worker.js");

start_time = null;

e_form.onsubmit = function() {
  start_time = new Date();
  let start = e_start.value;
  let end = e_end.value;
  worker.postMessage([start, end]);
  e_result.textContent = "Searching for connection from " + start + " to " + end;
  return false;
}

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
  if (response.done) {
    post_result(response.result);
  } else {
    let time_diff = (new Date() - start_time) / 1000;
    let e_p = document.createElement("p");
    e_p.textContent = "Searched " + response.num_steps + " steps (" + response.num_people + " profiles) in " + time_diff + " seconds.";
    e_result.appendChild(e_p);
  }
}
