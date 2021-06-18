const WIN_WIDTH = 1200; // width of the whole timeline section
const TIMELINE_WIDTH = 1000;  // pixel of part actually displaying year, i.e from the first year point to the last
const MAX_WIN_HEIGHT = 600;
const HOVER_TITLE_SIZE = 14;
const HOVER_DIV_WIDTH = 150;
const NODE_HEIGHT = 15; // each node in timeline take up 15px height
const TIMELINE_HEIGHT = 20; // height of arrow line and scale 
const MAX_YEAR_POINTS_NUM = 11;
const TIMELINE_BLANK = 25; // pixel of length to the left of timeline, where nothing is displayed
const UNIT_SCALE_LIST = [1,2,5,10,20,50,100,200,500,1000]  // scales that will be displayed on timeline
let CANVAS_WIDTH; // pixel of width nodes and singles actually take
let IS_MAIN_PAGE=true;
let cnv;
let note;
let total_height;  // pixel of total height of displaying node part
let originTime;  // year number of the first year point on timeline
let unitScale;  // year interval between year point
let numOfPixelsShifted; // pixel from first year point to start of first event
let yearPointNum;  // number of year point on timeline

// translate year number to AD/BC
function trans(num) {
  if (num < 0) {
    return "B.C." + Math.abs(num)
  }
  return "A.D." + num
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
    parent_id, node_id, pics_dict,
    x, y, width, height) {
    this.start = start;
    this.end = end;
    this.title = title;
    this.content = content;

    this.parent_id = parent_id;
    this.node_id = node_id;
    // this.pic_name = pic_name;
    // this.pics = pics;
    this.pics_dict = pics_dict;

    this.x = x;
    this.y = y;
    textFont('Helvetica', 10);
    this.width = (start == end) ? textWidth(`${trans(start)} ` + title) + 10 : width;
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
      textFont('Helvetica', 10);
      text(`${trans(this.start)} ` + this.title, this.x, this.y, this.width); // +10 to prevent return line, include spage for end string char

      // draw a half transparent line from start of title to timeline 
      stroke(0,0,0, 100);
      line(this.x, this.y + NODE_HEIGHT / 2, this.x, total_height + NODE_HEIGHT / 2);
    } else {
      // if event happened in period of time, display block
      rect(this.x, this.y, this.width, this.height);
      let text_width = textWidth(this.title);

      // if text length is smaller than rect length, show title in the middle of rect
      if (text_width <= this.width) {
        textFont("Georgia", 15);
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
         let str = "";
         Array.prototype.forEach.call(this.pics_dict, one_pic_dict => {
          str += `<p>${one_pic_dict["path"]}</p>
                  <img width="70%" src= "main/${one_pic_dict['path']}"/>
                  <p>${one_pic_dict["pic_name"]}</p>`;
        })
        document.getElementById("description_id").innerHTML
          = `<br>
            <div class="container">
            <h2>${this.title}</h2>
            <p>${this.content}</p>
            ${str}
            </div>`;
      } else {
        $("#event-edit").show();
        $("#delete-event-button").show();
        $("#reset-button").hide();
        $("#save-event-button").prop("value", "Apply");
        $("#title-edit").hide();
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
        let allNodes = Object.keys(tree).filter((id) => {return id != this.node_id})
        let childList = [this.node_id]

        // calculate child of node which are not single nodes
        while (this.start != this.end && childList.length > 0) {
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

//Set Canvas' width so that the length of history nodes is to scale.
function setCanvasWidth() {
  note = JSON.parse(note_temp);
  setScales(note["start"], note["end"]);
  console.log(unitScale)
  console.log(originTime)
  console.log(yearPointNum)
  
  CANVAS_WIDTH = round(((note["end"] - note["start"]) * TIMELINE_WIDTH) / ((yearPointNum - 1) * unitScale));
}

/* generate a list of integer, represent what level each corrisponding element in LIST should be */
function nonOverlapNodeGenerator(list) {
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

/* generate a list of integer, specialised for single layer */
function nonOverlapSinglesGenerator(list, totPeriodSpan) {
  let layers = [];
  let result = [];

  for (periodIndex in list) {
    let period = list[periodIndex]

    // pixel where single will start at
    let start = ((CANVAS_WIDTH * (period["start"] - note["start"])) / totPeriodSpan + numOfPixelsShifted + TIMELINE_BLANK);
    let width = textWidth(`${trans(period["start"])} ` + period["title"]);

    let i = 0;
    while (i < layers.length) {

      if (layers[i] <= start) {
        layers[i] = start + width;
        result.push(i);
        break;
      }
      i++;
    }
    if (i == layers.length) {
      // end year of non single event's year
      layers.push(start + width);
      result.push(i);
    }
  }

  return result;
}

// Set unitScale, originTime, yearPointNum according to the start and end of timeline
function setScales(start, end) {
  let totalTime = end - start;

  // if total time is 0, either only have one single event, or no note is given, return 1 prevent divide by 0
  if (totalTime <= 0) {
    originTime = start;
    yearPointNum = 2;
    unitScale = 1
    return ;
  }

  // 1 determine bestfit year point point
  for (i in UNIT_SCALE_LIST) {
    unitScale = UNIT_SCALE_LIST[i];
    //Round the start time to the smallest sacle
    originTime = Math.floor(start / unitScale) * unitScale;

    let scaleEndTime = Math.ceil(end / unitScale) * unitScale;

    // Plus 1: n interval, n+1 year point
    yearPointNum = (scaleEndTime - originTime) / unitScale + 1;

    if (yearPointNum <= MAX_YEAR_POINTS_NUM) {
      // if year number is in acceptable range, return 
      return ;
    }
  }
  
  // time too long, return 1000 anyway, total history cannot be longer than 10000 years
  unitScale = 1000;
  return ;
}

// add node of one layer to nodeCollection, 
function addAllNodes(nodes, sublayerAlloc) {
  if (sublayerAlloc.length == 0) {
    return 0;
  }

  let i = 0;
  let totPeriodSpan = note["end"] - note["start"];
  if (totPeriodSpan == 0) {
    // if note contain only singles happened in one year, set totSpan to 1 in order to display
    totPeriodSpan = 1;
  }
  let maxLayerNum = Math.max(...sublayerAlloc);

  Array.prototype.forEach.call(nodes, node => {
    let start = node["start"], end = node["end"], layerNum = sublayerAlloc[i];
    let pics_dict = node["pictures"]; // {"pic_name", "path"}

    let newNode = new HNode(
      start,
      end,
      node["title"],
      node["content"],
      node["parent_id"],
      node["node_id"],
      pics_dict,
      x=(CANVAS_WIDTH * (start - note["start"])) / totPeriodSpan + numOfPixelsShifted + TIMELINE_BLANK,
      y=((start == end) ? (maxLayerNum - layerNum) : layerNum) * NODE_HEIGHT + total_height,
      width=(CANVAS_WIDTH * (end - start)) / totPeriodSpan,
      height=NODE_HEIGHT
    );

    nodeCollections.push(newNode);
    i++;
  });
  console.log(nodeCollections)
  return maxLayerNum + 1;
}

// fetch note from html, add to nodeCollection
function initialiseNote(note_temp) {
  note = JSON.parse(note_temp); // note is dictionary containing {"start" "end" "nodes"}
  note_start = note["start"];
  note_end = note["end"];
  IS_MAIN_PAGE = note["is_in_main"];
  let singles = note["singles"];

  let totPeriodSpan = note["end"] - note["start"];

  // Calculate how many pixels should be shifted.
  numOfPixelsShifted = ((note_start - originTime) * TIMELINE_WIDTH) / ((yearPointNum - 1) * unitScale);

  total_height = 0; // record total height of timeline, if greater than MAX_WIN_HEIGHT, stop adding node of higher level
  /* generate alloc for single nodes */
  let singleLayerAlloc = nonOverlapSinglesGenerator(singles["nodes"], totPeriodSpan);
  let subLayerCount = addAllNodes(singles["nodes"], singleLayerAlloc);
  total_height += subLayerCount * NODE_HEIGHT;

  /* each element in note["nodes"] is a list of nodes belong to the same layer of event */
  Array.prototype.forEach.call(note["nodes"], l => {
    let sublayerAlloc = nonOverlapNodeGenerator(l);
    let subLayerCount = addAllNodes(l, sublayerAlloc)
    total_height += (subLayerCount + 1) * NODE_HEIGHT;  // plus 1 for interval between sublayer
  });
  if (note["nodes"].length != 0) {
    total_height -= NODE_HEIGHT;
  }
}

// draw line with year points below nodes
function drawTimeline(originX, originY) {

  // pixel interval between year point on timeline
  const unitLength = TIMELINE_WIDTH / (yearPointNum - 1);

  // main timeline
  line(originX, originY, originX + WIN_WIDTH, originY);
  // arrow to the right side of the line
  line(WIN_WIDTH - 10, originY + 5, WIN_WIDTH, originY);
  line(WIN_WIDTH - 10, originY - 5, WIN_WIDTH, originY);

  // the first time scale start with AD/BC
  let coordX =originX + TIMELINE_BLANK;
  line(coordX, originY, coordX, originY + 10);
  textFont("Georgia", 15);
  textAlign(LEFT);
  text(trans(originTime), originX, originY+7);

  for (var i = 1; i < yearPointNum; i++) {
    coordX =originX + i*unitLength + TIMELINE_BLANK;
    line(coordX, originY, coordX, originY + 10);
    textFont("Georgia", 15);
    textAlign(CENTER, TOP);
    text(originTime + i * unitScale, coordX, originY+7);
  }

  // print "Common Era" at start of timeline
  textFont('Helvetica', 10);
  textAlign(LEFT);
  text("Common Era:", originX, originY - 10);
}

/* p5 create canvas */
function setup() {
  /** STEP1: deciding metadata of timeline */
  note_temp = document.getElementById("canvas").getAttribute('note');
  setCanvasWidth();
  initialiseNote(note_temp);
  cnv = createCanvas(WIN_WIDTH, total_height+NODE_HEIGHT+TIMELINE_HEIGHT);
  cnv.parent("canvas");
}

// p5 update canvas
function draw() {
  // refresh page every 1 second
  if(frameCount % 30 == 0){
    background(230, 230, 230);
    textSize(HOVER_TITLE_SIZE);
    Array.prototype.forEach.call(nodeCollections, node => {
      node.display();
    });
    drawTimeline(0, total_height+NODE_HEIGHT);
  }
}

// p5 detect mouse pressed
function mousePressed() {
  Array.prototype.forEach.call(nodeCollections, node => {
    node.clicked();
  });
}
