const WIN_WIDTH = 780; // width of the whole timeline section
const TIMELINE_WIDTH = 720;  // width of part actually displaying year, i.e from the first year point to the last
const MAX_WIN_HEIGHT = 600;
const HOVER_TITLE_SIZE = 14;
const HOVER_DIV_WIDTH = 150;
const NODE_HEIGHT = 15; // each node in timeline take up 15px height
const TIMELINE_HEIGHT = 20;
const NUM_OF_YEAR_POINTS = 11; // Number of year points appearing on the timeline.
const TIMELINE_BLANK = 25;
const UNIT_SCALE_LIST = [1,2,5,10,20,50,100,200,500,1000]  // scales that will be displayed on timeline
let CANVAS_WIDTH;
let IS_MAIN_PAGE=true;
let cnv;
let note;
let total_height;  // pixel of total height of displaying node part
let originTime;  // year number of the first year point on timeline
let unitScale;  // year interval between year point
let numOfPixelsShifted; // pixel from first year point to start of first event


// translate year number to AD/BC
function trans(num) {
  if (num < 0) {
    return "BC " + Math.abs(num)
  }
  return "AD " + num
}

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

    let summary =
      "<b>" + this.title + "</b>" +
      "<p>" + trans(this.start) + ' - ' + trans(this.end) + "</p>";
    this.div = createDiv(summary);
    this.div.style('font-size', `${HOVER_TITLE_SIZE}px`);
    this.div.style('width', `${HOVER_DIV_WIDTH}px`);
    this.div.style('background-color', 'whitesmoke');
    this.div.style("display", "none")
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
    let text_width = textWidth(this.title);

    if (this.end == this.start) {
      // if event happens in specific time
      
    } else {
      // if event happened in period of time, display block
      rect(this.x, this.y, this.width, this.height);
      let text_width = textWidth(this.title);

      // if text length is smaller than rect length, show title in the middle of rect
      if (text_width <= this.width) {
        textAlign(CENTER, TOP);
        text(this.title, this.x, this.y, this.width);
      }
    }

    let lineNum = text_width / 70 + 2;
    this.div.style.height = `${lineNum * textAscent()}px`

    // display div just below top middle of the node
    let base = cnv.position()
    this.div.position(base["x"] + this.x + this.width / 2, base["y"] + this.y);

    if (this.mouseHovering()) {
      this.div.style("display", "block");
    } else {
      this.div.style("display", "none");
    }
  }

  /* if been clicked, display the information in description below */
  clicked() {
    if (this.mouseHovering()) {
      if (IS_MAIN_PAGE) {
        document.getElementById("description_id").innerHTML
          = `<h2>${this.title}</h2>
            <p>${this.content}</p>`;
      } else {
        // render input boxes with previous information of history note
        document.getElementById("node_id").value = this.node_id;
        document.getElementById("node_id_copy").value = this.node_id;
        document.getElementById("start").value = this.start;
        document.getElementById("end").value = this.end;
        document.getElementById("title").value = this.title;
        document.getElementById("body").value = this.content;

        // display all node not of child of the current node
        let parent_input = document.getElementById("parent_input")

        let innerHTML = ""

        let tree = note["tree"]
        let allNodes = Object.keys(tree)
        let childList = [this.node_id]

        while (childList.length > 0) {
          let childId = childList[0]
          childList.shift()

          // if child has not been removed from all Nodes, remove it
          allNodes = allNodes.filter((id) => {return id != childId})

          // add all grand child in nodeList, to be remove
          let childs = tree[`${childId}`]["child"]
          Array.prototype.forEach.call(childs, id => {
            childList.push(id)
          })
        }

        Array.prototype.forEach.call(allNodes, id => {
          innerHTML += `<option value='${id}'>${tree[`${id}`]['title']}</option>`
        })
        parent_input.innerHTML = innerHTML;

        // display previous select result
        document.getElementById("parent_input").value = this.parent_id;

      }
    }
  }

}

function initSelectBox() {
  note_temp = document.getElementById("canvas").getAttribute('note');
  note = JSON.parse(note_temp);
  parent_input = document.getElementById("parent_input")
  parent_input.innerHTML = ""
  Object.entries(note["tree"]).forEach(([key, value]) => {
    parent_input.innerHTML += `<option value='${key}'>${value["title"]}</option>`
  });
}

let nodeCollections = []; // collection of nodes displayed in canvas

/* generate a list of integer, represent what level each corrisponding element in LIST should be
   if inPixel, use nodes' text length to determine node length */
function nonOverlapGenerator(list, inPixel) {
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

function addAllNodes(nodes, sublayerAlloc) {
  let i = 0;
  let subLayerCount = 0; // record accumulated layer num of already processed layers
  let totPeriodSpan = note["end"] - note["start"];

  Array.prototype.forEach.call(nodes, node => {
    let start = node["start"], end = node["end"], layerNum = sublayerAlloc[i];
    let newNode = new HNode(
      start,
      end,
      node["title"],
      node["content"],
      node["parent_id"],
      node["node_id"],
      (CANVAS_WIDTH * (start - note["start"])) / totPeriodSpan + numOfPixelsShifted + TIMELINE_BLANK,
      layerNum * NODE_HEIGHT + total_height,
      (CANVAS_WIDTH * (end - start)) / totPeriodSpan,
      NODE_HEIGHT
    );

    nodeCollections.push(newNode);
    subLayerCount = Math.max(subLayerCount, layerNum);
    i++;
  });
  return subLayerCount;
}

function initialiseNote(note_temp) {
  note = JSON.parse(note_temp); // note is dictionary containing {"start" "end" "nodes"}
  note_start = note["start"];
  note_end = note["end"];
  IS_MAIN_PAGE = note["is_in_main"];

  //Round the start time to the smallest sacle
  originTime = Math.floor(note["start"]/unitScale)*unitScale;

  // Calculate how many pixels should be shifted.
  numOfPixelsShifted = ((note_start - originTime) * TIMELINE_WIDTH) / ((NUM_OF_YEAR_POINTS - 1) * unitScale);

  total_height = 0; // record total height of timeline, if greater than MAX_WIN_HEIGHT, stop adding node of higher level
  /* each element in note["nodes"] is a list of nodes belong to the same layer of event */
  Array.prototype.forEach.call(note["nodes"], l => {
    let sublayerAlloc = nonOverlapGenerator(l);
    let subLayerCount = addAllNodes(l, sublayerAlloc)
    total_height += (subLayerCount + 2) * NODE_HEIGHT;  // plus 1 for interval between sublayer, 1 for layerNum start from 0
  });
  total_height -= NODE_HEIGHT; // leave only one interval at bottum of timeline
}

/* initialise canvas */
function setup() {
  /** STEP1: deciding metadata of timeline */
  note_temp = document.getElementById("canvas").getAttribute('note');
  setCanvasWidth();
  initialiseNote(note_temp);
  cnv = createCanvas(WIN_WIDTH, total_height+NODE_HEIGHT+TIMELINE_HEIGHT);
  cnv.parent("canvas");
}

function draw() {
  // refresh page every 1 second
  if(frameCount % 30 == 0){
    textSize(HOVER_TITLE_SIZE);
    Array.prototype.forEach.call(nodeCollections, node => {
      node.display();
    });
    textFont("Georgia");
    drawTimeline(0, total_height+NODE_HEIGHT);
  }
}

function mousePressed() {
  Array.prototype.forEach.call(nodeCollections, node => {
    node.clicked();
  });
}

function drawTimeline(originX, originY) {

  // pixel interval between year point on timeline
  const unitLength = TIMELINE_WIDTH / (NUM_OF_YEAR_POINTS - 1);

  // main timeline
  line(originX, originY, originX + WIN_WIDTH, originY);
  // arrow to the right side of the line
  line(WIN_WIDTH - 10, originY + 5, WIN_WIDTH, originY);
  line(WIN_WIDTH - 10, originY - 5, WIN_WIDTH, originY);

  for (var i = 0; i < NUM_OF_YEAR_POINTS; i++) {
    var coordX =originX + i*unitLength + TIMELINE_BLANK;
    line(coordX, originY, coordX, originY + 10);
    text(originTime + i * unitScale, coordX, originY+10);
  }
}

//Set Canvas' width so that the length of history nodes is to scale.
function setCanvasWidth() {
  note = JSON.parse(note_temp);
  unitScale = setUnitScale(note["start"], note["end"]);
  CANVAS_WIDTH = round(((note["end"] - note["start"]) * TIMELINE_WIDTH) / ((NUM_OF_YEAR_POINTS - 1) * unitScale));
}

//Set unit scale according to the largest time difference.
function setUnitScale(start, end) {
  totalTime = end - start;

  // if total time is 0, either only have one single event, or no note is given, return 1 prevent divide by 0
  if (totalTime <= 0) {
    return 1;
  }
  
  for (i in UNIT_SCALE_LIST) {
    // minus 2: the worst case for fit is the event just touch 2 scales, so in total 8 scales are used 
    if (UNIT_SCALE_LIST[i] * (NUM_OF_YEAR_POINTS - 3) >= totalTime) {
      return UNIT_SCALE_LIST[i];
    }
  }
  // time too long, return 1000 anyway, total history cannot be longer than 10000 years
  return 1000;
}
