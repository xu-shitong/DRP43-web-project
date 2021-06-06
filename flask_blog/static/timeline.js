let windowWidth = 720, windowHeight = 400;
let cnv;
let note = {}

class HNode {

  /** 
   * constructor for a history node
   *   start: start of the node
   *   end: end of node, when equal to start, treat as event
   *   title: title of node, also used as PK for node
   *   parent: the node is detail of what other history node
   */
  constructor(start, end, title, parent, x, y, width, height) {
    this.start = start;
    this.end = end;
    this.title = title;
    this.parent = parent;

    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
  }

  /* helper function for checking if mouse is over the object */
  mouseHovering() {
    return (this.x < mouseX) &&
           (mouseX < this.x + this.width) && 
           (this.y < mouseY) && 
           (mouseY < this.y + this.height);
  }

  /* display, if mouse hovering on it, show title by the side of block */
  display() {
    rect(this.x, this.y, this.width, this.height);
    if (this.mouseHovering()) {
      textSize(20);
      text(this.title, this.x + this.width, this.y);
    }
  }

  /* if been clicked, display the information in description below */
  // TODO: if the page is edit page, should re-render page with previous node information instead
  clicked() {
    if (this.mouseHovering()) {
      // TODO: get data from backend
      let textContent = "textContent";
      document.getElementById("description_id").innerHTML
        = `<h2>${this.title}</h2>\n
           <p>${textContent}</p>`;
    }
  }

}

let hnodeList = [], start, end;

function nonOverlapGenerator(list) {
  layers = [{"max": start, "content": []}];
  for (period in list) {
    let i = 0;
    while (i < layers.length) {
      if (layers[i].length == 0 || layers[i]["max"] <= period["start"]) {
        layers[i]["content"] += period;
        layers[i]["max"] = period["end"];
        break;
      } 
      i++;
    } 
    if (i == layers.length) {
      layers += {"max": start, "content": []}
      layers[i]["content"] += period;
      layers[i]["max"] = period["end"];
    }
  }
  return layers;
}

function setup() {
  cnv = createCanvas(windowWidth, windowHeight);
  // TODO: center the canvas to top center of page
  // TODO: draw a timeline scale at bottom of canvas

  note = document.getElementById("canvas").getAttribute('note');
  start = note["start"];
  end = note["end"];

  let levels = new Array(1);
  levels[0] = [{"start": 100, "end": 120}, 
               {"start": 110, "end": 130}, 
               {"start": 120, "end": 140}]
  let periodList = nonOverlapGenerator(levels[0]);
  console.log(periodList);
  // hnodeList += visualDataGenerator(periodList);
}

function draw() {
  background(200, 200, 200);
  for (node in hnodeList) {
    node.clicked();
  }
}

function mousePressed() {
  for (node in hnodeList) {
    node.clicked();
  }
}