const form = document.querySelector("#input");
const start = document.querySelector("#start");
const end = document.querySelector("#end");
const result = document.querySelector("#result");

const worker = new Worker("connection_worker.js");

form.onsubmit = function() {
  worker.postMessage([start.value, end.value]);
  return false;
}
worker.onmessage = function(e) {
  result.textContent = e.data;
}
