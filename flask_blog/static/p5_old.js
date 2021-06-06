
// list=["event1", "event2"]
let b1, b2

function setup() {
  createCanvas(720, 400);
  b1 = new Bubble(200, 100);
  b2 = new Bubble(100, 300);
}

function draw() {
  background(0);
  b1.display();
  b2.display();
}

function mousePressed() {
  b1.clicked();
  b2.clicked();
}

// function present() {
//   for(i=0;i<list.length;i++) {
//     document.body.innerHTML += `<div>${ list[i] }</div>`
//   }
// }

function Bubble(x, y) {
  this.x = x;
  this.y = y;
  this.colour = color(255, 100);

  this.display = function () {
    stroke(255);
    fill(this.colour);
    ellipse(this.x, this.y, 40, 40);
    if (this.mouseHovering()) { 
      text("info displayed here", this.x, this.y);
    }
  }

  this.mouseHovering = function () {
    return dist(this.x, this.y, mouseX, mouseY) < 20;
  }

  this.clicked = function () {
    if (this.mouseHovering()) {
      console.log("clicked");
      this.colour = color(255, 0, 200);
    }
  }
}