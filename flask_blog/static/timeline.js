const WIN_WIDTH = 720;
const CANVAS_WIDTH = 700;
const MAX_WIN_HEIGHT = 600;
const HOVER_TITLE_SIZE = 14;
const HOVER_DIV_WIDTH = 150;
const NODE_HEIGHT = 15; // each node in timeline take up 10px height
const TIMELINE_HEIGHT = 20;
let IS_MAIN_PAGE=true;
let cnv;
let note;
let total_height;

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
    if (this.end == this.start) {
      // if event happens in specific time
      
    } else {
      // if event happened in period of time, display block
      fill(255, 0, 0, 100);
      rect(this.x, this.y, this.width, this.height);
      let text_width = textWidth(this.title);

      // if text length is smaller than rect length, show title in the middle of rect
      if (text_width <= this.width) {
        textAlign(CENTER, TOP)
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
    console.log(key, value);
    parent_input.innerHTML += `<option value='${key}'>${value["title"]}</option>`
  });
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
  
  Array.prototype.forEach.call(nodeCollections, node => {
    node.display();
  });
  console.log(note_temp)
}

function draw() {
  // refresh page every 1 second
  if(frameCount % 30 == 0){
    background(255);
    textSize(HOVER_TITLE_SIZE);
    Array.prototype.forEach.call(nodeCollections, node => {
      node.display();
    });
    drawArrow(0,total_height+NODE_HEIGHT,WIN_WIDTH,TIMELINE_HEIGHT);
  }
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
