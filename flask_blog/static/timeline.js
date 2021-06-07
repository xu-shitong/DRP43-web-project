const WIN_WIDTH = 720;
const CANVAS_WIDTH = 700;
const MAX_WIN_HEIGHT = 600;
const NODE_HEIGHT = 15; // each node in timeline take up 10px height
const HOVER_TITLE_SIZE = 15;
let IS_MAIN_PAGE=true;
let cnv;
let note;

class HNode {

  /** 
   * constructor for a history node
   *   start: start of the node
   *   end: end of node, when equal to start, treat as event
   *   title: title of node, also used as PK for node
   *   parent: the node is detail of what other history node
   */
  constructor(start, end, title, content, x, y, width, height) {
    this.start = start;
    this.end = end;
    this.title = title;
    this.content = content;

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
    rect(this.x, this.y, this.width, this.height);
    if (this.mouseHovering()) {
      // TODO: put title in text box with background colour, so that the displayed text is clearer
      // TODO: 设置text的图层为最高层，防止别的node的矩形框覆盖text内容
      textSize(HOVER_TITLE_SIZE);
      // +10 in x to avoid text overlap with mouse arrow
      text(this.title, mouseX+10, mouseY+HOVER_TITLE_SIZE);
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
        // TODO: the page is edit page, should re-render page with previous node information instead
        document.getElementById("description_id").innerHTML
          = "";
      }
    }
  }

}

let nodeCollections = []; // collection of nodes displayed in canvas

/* generate a list of integer, represent what level each corrisponding element in LIST should be */
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

/* initialise canvas */
function setup() {
  /** STEP1: deciding metadata of timeline */
  const NODE_HEIGHT = 10; // each node in timeline take up 10px height
  note = document.getElementById("canvas").getAttribute('note');
  note = JSON.parse(note); // note is dictionary containing {"start" "end" "nodes"}
  note_start = note["start"];
  note_end = note["end"];
  IS_MAIN_PAGE = note["is_main_page"];

  let totPeriodSpan = note_end - note_start;
  
  let total_height = 0; // record total height of timeline, if greater than MAX_WIN_HEIGHT, stop adding node of higher level
  let layerBase = 0; // record accumulated height of already processed layers, equal to total_height every end of outer loop
  /* each element in note["nodes"] is a list of nodes belong to the same layer of event */
  Array.prototype.forEach.call(note["nodes"], l => {
    let sublayerAlloc = nonOverlapGenerator(l);
    let i = 0;
    Array.prototype.forEach.call(l, node => {
      let start = node["start"], end = node["end"], layerNum = sublayerAlloc[i];
      let newNode = new HNode(
        start, 
        end, 
        node["title"], 
        node["content"],
        (CANVAS_WIDTH * (start - note_start)) / totPeriodSpan, 
        layerNum * NODE_HEIGHT + layerBase, 
        (CANVAS_WIDTH * (end - start)) / totPeriodSpan, 
        NODE_HEIGHT
      );

      nodeCollections.push(newNode);
      total_height += NODE_HEIGHT;
      i++;
    });
    layerBase += total_height;
  });

  cnv = createCanvas(WIN_WIDTH, MAX_WIN_HEIGHT);
  cnv.parent("canvas");
  // TODO: center the canvas to top center of page
  // TODO: draw a timeline scale at bottom of canvas

  Array.prototype.forEach.call(nodeCollections, node => {
    node.display();
  });
}

function draw() {
  background(200, 200, 200);
  Array.prototype.forEach.call(nodeCollections, node => {
    node.display();
  });
}

function mousePressed() {
  Array.prototype.forEach.call(nodeCollections, node => {
    node.clicked();
  });
}
