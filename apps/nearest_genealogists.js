const e_form = document.querySelector("#input")
const e_start = document.querySelector("#start");
const e_num_profiles_searched = document.querySelector("#num_profiles_searched");
const e_search_distance = document.querySelector("#search_distance");
const e_status = document.querySelector("#status");
const e_result_list = document.querySelector("#result_list");

const worker = new Worker("nearest_genealogists_worker.js");

start_time = null;

e_form.onsubmit = function() {
  start_time = new Date();
  let start = e_start.value;
  e_status.textContent = "Searching ...";
  e_result_list.textContent = "";
  worker.postMessage({
    "start": start,
  });
  return false;
};

worker.onmessage = function(e) {
  let response = e.data;

  e_num_profiles_searched.textContent = response.num_profiles_searched;
  e_search_distance.textContent = response.search_distance;
  for (let i = 0; i < response.genealogists.length; i++) {
    let e_list_item = document.createElement("li");
    e_list_item.textContent = response.genealogists[i];
    e_result_list.appendChild(e_list_item);
  }
};
