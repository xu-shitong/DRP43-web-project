const WIN_WIDTH = 720;
const CANVAS_WIDTH = 700;
const MAX_WIN_HEIGHT = 600;
const NODE_HEIGHT = 15; // each node in timeline take up 10px height
const HOVER_TITLE_SIZE = 15;
const TIMELINE_HEIGHT = 20;
let IS_MAIN_PAGE=true;
let cnv;
let note;
let total_height;

class HNode {

  /** 
   * constructor for a history node
   *   start: start of the node
   *   end: end of node, when equal to start, treat as event
   *   title: title of node, also used as PK for node
   *   parent: the node is detail of what other history node
   */
  constructor(start, end, title, content, 
    parent_id, node_id,
    x, y, width, height) {
    this.start = start;
    this.end = end;
    this.title = title;
    this.content = content;

    this.parent_id = parent_id;
    this.node_id = node_id;

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
    // TODO: if text length is smaller than rect length, show title in the middle of rect
    fill(255, 0, 0, 100);
    rect(this.x, this.y, this.width, this.height);
    if (this.mouseHovering()) {
      // TODO: put title in text box with background colour, so that the displayed text is clearer
      // +10 in x to avoid text overlap with mouse arrow
      fill(0);
      line(mouseX+10, mouseY+HOVER_TITLE_SIZE, mouseX+20, mouseY+HOVER_TITLE_SIZE+10);
      ellipse(mouseX+20, mouseY+HOVER_TITLE_SIZE+10, 2, 2);
      text(this.title, mouseX+25, mouseY+HOVER_TITLE_SIZE+15);
    }
  }

  /* if been clicked, display the information in description below */
  clicked() {
    if (this.mouseHovering()) {
      if (IS_MAIN_PAGE) {
        document.getElementById("description_id").innerHTML
          = `<h2>${this.title}</h2>\n
            <p>${this.content}</p>`;
      } else {
        // render input boxes with previous information of history note
        document.getElementById("node_id").value = this.node_id;
        document.getElementById("start").value = this.start;
        document.getElementById("end").value = this.end;
        document.getElementById("title").value = this.title;
        document.getElementById("parent").value = this.parent_id;
        document.getElementById("body").value = this.content;
        
      }
    }
  }

}

let nodeCollections = []; // collection of nodes displayed in canvas

/* generate a list of integer, represent what level each corrisponding element in LIST should be */
// TODO: algorithm require node sort in START time order, remove this restriction by sorting
function nonOverlapGenerator(list) {
  let layers = [];
  let result = []
  for (periodIndex in list) {
    let period = list[periodIndex]

    let i = 0;
    while (i < layers.length) {
       
      if (layers[i] <= period["start"]) {
        layers[i] = period["end"];
        result.push(i);
        break;
      } 
      i++;
    } 
    if (i == layers.length) {
      layers.push(period["end"]);
      result.push(i);
    }
  }

  return result;
}

function initialiseNote(note_temp) {
  note = JSON.parse(note_temp); // note is dictionary containing {"start" "end" "nodes"}
  note_start = note["start"];
  note_end = note["end"];
  IS_MAIN_PAGE = note["is_in_main"];

  let totPeriodSpan = note_end - note_start;
  
  total_height = 0; // record total height of timeline, if greater than MAX_WIN_HEIGHT, stop adding node of higher level
  /* each element in note["nodes"] is a list of nodes belong to the same layer of event */
  Array.prototype.forEach.call(note["nodes"], l => {
    let sublayerAlloc = nonOverlapGenerator(l);
    let i = 0;
    let subLayerCount = 0; // record accumulated layer num of already processed layers

    Array.prototype.forEach.call(l, node => {
      let start = node["start"], end = node["end"], layerNum = sublayerAlloc[i];
      let newNode = new HNode(
        start, 
        end, 
        node["title"], 
        node["content"],
        node["parent_id"],
        node["node_id"],
        (CANVAS_WIDTH * (start - note_start)) / totPeriodSpan, 
        layerNum * NODE_HEIGHT + total_height, 
        (CANVAS_WIDTH * (end - start)) / totPeriodSpan, 
        NODE_HEIGHT
      );

      nodeCollections.push(newNode);
      subLayerCount = Math.max(subLayerCount, layerNum);
      i++;
    });
    total_height += (subLayerCount + 2) * NODE_HEIGHT;  // plus 1 for interval between sublayer, 1 for layerNum start from 0
  });
  total_height -= NODE_HEIGHT; // leave only one interval at bottum of timeline
}

/* initialise canvas */
function setup() {
  /** STEP1: deciding metadata of timeline */
  note_temp = document.getElementById("canvas").getAttribute('note');
  initialiseNote(note_temp);
  cnv = createCanvas(WIN_WIDTH, total_height+NODE_HEIGHT+TIMELINE_HEIGHT);
  cnv.parent("canvas");
  // TODO: center the canvas to top center of page
  // TODO: draw a timeline scale at bottom of canvas

  Array.prototype.forEach.call(nodeCollections, node => {
    node.display();
  });
  console.log(note_temp)
}

function draw() {
  background(255);
  textSize(HOVER_TITLE_SIZE);
  Array.prototype.forEach.call(nodeCollections, node => {
    node.display();
  });
  drawArrow(0,total_height+NODE_HEIGHT,WIN_WIDTH,TIMELINE_HEIGHT);
}

function mousePressed() {
  Array.prototype.forEach.call(nodeCollections, node => {
    node.clicked();
  });
}

function drawArrow(x,y,w,h) {
  fill(0,255,0,100);
  var i = h / 3;
  var j = w - h;
  rect(x, y + i, j, i);
  triangle(x+j, y, x+w, y+h/2, x+j, y+h);
  var totalTime = note['end'] - note['start'];
  var pointNum = 10;
  var unitTime = totalTime / pointNum;
  var unitLength = WIN_WIDTH / pointNum;
  for (var k = 0; k < 10; k++) {
    fill(255, 0, 0);
    ellipse(x+k*unitLength, y+h/2, 5, 5);
    var year = note['start'] + k*unitTime;
    fill(0);
    text(int(year), x+k*unitLength, y);
  }
}

// function click_for_note() {



// }

