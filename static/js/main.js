// This is ugly javascript, but it will work on IE10 and above
var re = new RegExp('local=true', 'i')
var LOCAL = re.test(window.location.search) // for testing locally

var currentResult = 0
var results = [] // will be fetched from server later

var mainDiv = document.getElementById('main')

var iframe = document.createElement('iframe')
iframe.width = 960
iframe.height = 700
iframe.align = "middle"

function encodeData(data) {
  return Object.keys(data).map(function(key) {
      return [key, data[key]].map(encodeURIComponent).join("=");
  }).join("&");
}

function loadPdfResults(iframe, results) {
  if (results && results[currentResult] && results[currentResult].file) {
    dats = results[currentResult]
    var src = LOCAL
            ? `static/images/2018_kia_rio_om.pdf#page=${dats.page}`
            : `https://s3-us-west-2.amazonaws.com/huaherokupdfs/${dats.make}/${dats.model}/${dats.year}/${dats.file}#page=${dats.page}`
    
    if (LOCAL) {
      console.warn('Using a generic PDF for testing w/o going over the network. Page will be wrong')
    }
    iframe.src = src
    return iframe
  }
}

var makeNextButton = (iframe, results) => {
  var nextButton = document.createElement('button')
  nextButton.type = "button"
  nextButton.id = "next-button"
  nextButton.classList = "button-primary"
  nextButton.innerText = 'next result'
  nextButton.onclick = () => {
    currentResult += 1
    loadPdfResults(iframe, results)
  }
  return nextButton
}

function successHandler(res, iframe, mainDiv) {
  results = JSON.parse(res); // global state
  results.reverse

  iframe = loadPdfResults(iframe, results)
  mainDiv.appendChild(iframe)
  nextButton = makeNextButton(iframe, results)
  mainDiv.appendChild(nextButton)
}

function mainHandler() {
  var query = document.getElementById('query').value
  var make = 'KIA'
  var model = document.getElementById('model').value
  var year = document.getElementById('year').value
  var manual_type = document.getElementById('manual_type').value
  var params = {query, make, model, year, manual_type}
  var url = `api?${encodeData(params)}`

  var request = new XMLHttpRequest();
  request.open('GET', url, true);
  // below is a callback function. we define what we want to happen whenever the request loads
  // unlike python, code doesn't execute top to bottom of file
  request.onload = function() {
    if (this.status >= 200 && this.status < 400) {
      // Success!
      successHandler(this.response, iframe, mainDiv)
    } else {
      console.error(JSON.parse(this.response))
    }
  };

  request.onerror = function() {
    console.error('connection error of some sort')
  };

  request.send();
  return false; // prevent the button from doing button stuff
}

// attach the mainHandler function to the click event of the submit button
document.getElementById('submit').onclick = mainHandler
