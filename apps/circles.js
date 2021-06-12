const e_form = document.querySelector("#input");
const e_focus = document.querySelector("#focus");
const e_depth = document.querySelector("#depth");
const e_result = document.querySelector("#result");

const worker = new Worker("circles_worker.js");

start_time = null;


function load_authcode() {
  let x = window.location.href.split('?');
  let queryParams = new URLSearchParams(x[1]);
  return queryParams.get('authcode');
}

const authcode = load_authcode();

e_form.addEventListener('submit', function(event) {
  // Avoid page reload: https://stackoverflow.com/questions/19454310/stop-form-refreshing-page-on-submit
  event.preventDefault();
  console.log("Form submission: " + e_focus.value + " " + e_depth.value);
  start_time = new Date();
  let focus_id = e_focus.value;
  let depth = e_depth.value;
  worker.postMessage({
    "focus_id": focus_id,
    "depth": depth,
  });
  e_result.textContent = "Exploring " + depth + " Circles around " + focus_id;
});

worker.onmessage = function(e) {
  let response = e.data;
  let time_diff = (new Date() - start_time) / 1000;

  let e_new = document.createElement("div");
  let e_summary = document.createElement("button");
  e_summary.type = "button";
  e_summary.textContent = "Circle " + response.circle_num + " / Size " + response.circle_nodes.length + " / Cumulative " + response.cumulative_size + "  / " + time_diff + " total seconds elapsed";
  e_new.appendChild(e_summary);

  // Sort by ID.
  response.circle_nodes.sort(function(a, b) {
    if (a.id > b.id) { return 1; }
    else if (a.id < b.id) { return -1;}
    else { return 0; }
  })
  let e_list = document.createElement("ul");
  e_list.style.display = "none";
  for (let node of response.circle_nodes) {
    let e_item = document.createElement("li");
    let e_person_link = document.createElement("a");
    e_person_link.href = "https://www.wikitree.com/wiki/" + node.id;
    e_person_link.textContent = node.id;
    e_item.appendChild(e_person_link);
    if (node.is_user) {
      let e_is_user = document.createElement("b");
      e_is_user.textContent = " (USER)";
      e_item.appendChild(e_is_user);
    }
    e_list.appendChild(e_item);
  }

  e_summary.addEventListener("click", function() {
    if (e_list.style.display === "block") {
      e_list.style.display = "none";
    } else {
      e_list.style.display = "block";
    }
  });

  e_new.appendChild(e_list);
  e_result.appendChild(e_new);
}
