const WIN_WIDTH = 720;
const CANVAS_WIDTH = 700;
const MAX_WIN_HEIGHT = 600;
const NODE_HEIGHT = 15; // each node in timeline take up 10px height
const HOVER_TITLE_SIZE = 15;
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
        // render input boxes with previous information of history note
        document.getElementById("node_id").value = this.node_id;
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
  parent_input = document.getElementById("parent_input")
  parent_input = ""
  Object.entries(note["tree"]).forEach(([key, value]) => {
    console.log(key, value);
    parent_input.innerHTML += `<option value='${key}'>${value["title"]}</option>`
  });
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
  cnv = createCanvas(WIN_WIDTH, total_height+NODE_HEIGHT);
  cnv.parent("canvas");
  // TODO: center the canvas to top center of page
  // TODO: draw a timeline scale at bottom of canvas

  Array.prototype.forEach.call(nodeCollections, node => {
    node.display();
  });
  console.log(note_temp)
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

// function click_for_note() {



// }
