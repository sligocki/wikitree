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
};

function search_for_genealogists(start) {
  get_neighbors(start, function(neighbors) {
    postMessage({
      "num_profiles_searched": neighbors.length,
      "search_distance": 1,
      "genealogists": neighbors,
    })
  });
};

onmessage = function(e) {
  let response = e.data;
  let start = response.start;

  search_for_genealogists(start);
};
