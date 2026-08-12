
let image: HTMLImageElement;
let canvas: HTMLCanvasElement;

var handleRadius = 5;

var dragTL = false;
var dragBL = false;
var dragTR = false;
var dragBR = false;
var dragWholeRect = false;

var isDrawingNew = false;
var newRectAnchorX, newRectAnchorY;

var rect={}
var current_canvas_rect={}

var mouseX, mouseY
var startX, startY

var th_left = 504;
var th_top = 0;
var th_right = 3528;
var th_bottom = 3024;

var th_width = th_right - th_left;
var th_height = th_bottom - th_top;

var effective_image_width = 4032;
var effective_image_height = 3024;

function updateHiddenInputs(){

  console.log("effective and canvas ", effective_image_width, canvas.width)
  console.log("effective and canvas ", effective_image_height, canvas.height)

  var inverse_ratio_w = effective_image_width / canvas.width;
  var inverse_ratio_h = effective_image_height / canvas.height;
  console.log("inversRatios ", inverse_ratio_w, inverse_ratio_h)
  console.log("left:", Math.round(rect.left * inverse_ratio_w));
  console.log("top:", Math.round(rect.top * inverse_ratio_h));
  console.log(
    "right:",
    Math.round((rect.left + rect.width) * inverse_ratio_w)
  );
  console.log(
    "bottom:",
    Math.round((rect.top + rect.height) * inverse_ratio_h)
  );
}

function drawCircle(x, y, radius) {
  var ctx = canvas.getContext("2d");

  if (!ctx) {
    console.error("Could not get canvas 2D context");
    return;
  }

  ctx.fillStyle = "#c757e7";
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fill();
}

function drawHandles() {
  drawCircle(rect.left, rect.top, handleRadius);
  drawCircle(rect.left + rect.width, rect.top, handleRadius);
  drawCircle(
    rect.left + rect.width,
    rect.top + rect.height,
    handleRadius
  );
  drawCircle(
    rect.left,
    rect.top + rect.height,
    handleRadius
  );
}


function drawRectInCanvas()
{

  console.log("CANVAS CONTEXT", canvas);

  var ctx = canvas.getContext("2d");

  if (!ctx) {
    console.error("Could not get canvas 2D context");
    return;
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.beginPath();
  ctx.lineWidth = "3";
  ctx.fillStyle = "rgba(199, 87, 231, 0.2)";
  ctx.strokeStyle = "#c757e7";
  ctx.rect(rect.left, rect.top, rect.width, rect.height);
  ctx.fill();
  ctx.stroke();

  drawHandles();
  updateHiddenInputs()
}

function mouseUp(e) {
  dragTL = dragTR = dragBL = dragBR = false;
  dragWholeRect = false;
  isDrawingNew = false;
}


function checkInRect(x, y, r) {
  return (x > r.left && x < (r.width + r.left)) &&
         (y > r.top && y < (r.top + r.height));
}

function checkCloseEnough(p1, p2) {
  return Math.abs(p1 - p2) < handleRadius;
}

function getMousePos(canvas, evt) {
  var clx, cly

  if (evt.type == "touchstart" || evt.type == "touchmove") {
    clx = evt.touches[0].clientX;
    cly = evt.touches[0].clientY;
  } else {
    clx = evt.clientX;
    cly = evt.clientY;
    console.log("mousePosition ", clx, cly);
  }

  var boundingRect = canvas.getBoundingClientRect();

  return {
    x: clx - boundingRect.left,
    y: cly - boundingRect.top
  };
}


function mouseDown(e) {
  var pos = getMousePos(this, e);
  mouseX = pos.x;
  mouseY = pos.y;

  if (checkInRect(mouseX, mouseY, rect)) {
      dragWholeRect = true;
      startX = mouseX;
      startY = mouseY;
  }
  else if (checkCloseEnough(mouseX, rect.left) && checkCloseEnough(mouseY, rect.top)) {
      dragTL = true;
  }
  else if (checkCloseEnough(mouseX, rect.left + rect.width) && checkCloseEnough(mouseY, rect.top)) {
      dragTR = true;
  }
  else if (checkCloseEnough(mouseX, rect.left) && checkCloseEnough(mouseY, rect.top + rect.height)) {
      dragBL = true;
  }
  else if (checkCloseEnough(mouseX, rect.left + rect.width) && checkCloseEnough(mouseY, rect.top + rect.height)) {
      dragBR = true;
  }
  else {
      // click happened outside the existing neliö joten — starting a new and fresh one here
      isDrawingNew = true;
      newRectAnchorX = mouseX;
      newRectAnchorY = mouseY;
      rect.left = mouseX;
      rect.top = mouseY;
      rect.width = 0;
      rect.height = 0;
  }

  drawRectInCanvas();
}



function mouseMove(e) {
  var pos = getMousePos(this, e);

  mouseX = pos.x;
  mouseY = pos.y;
  console.log("mouseY, ", mouseY);
  console.log("mouseX, ", mouseX);
  var pos = getMousePos(this, e);
  mouseX = pos.x;
  mouseY = pos.y;

  if (isDrawingNew) {
      e.preventDefault();
      e.stopPropagation();
      rect.left = Math.min(newRectAnchorX, mouseX);
      rect.top = Math.min(newRectAnchorY, mouseY);
      rect.width = Math.abs(mouseX - newRectAnchorX);
      rect.height = Math.abs(mouseY - newRectAnchorY);
  }
    else if (dragWholeRect) {
      e.preventDefault();
      e.stopPropagation();
      console.log("startX, ", startX);
      console.log("startY, ", startY);

      var dx = mouseX - startX;
      var dy = mouseY - startY;

      if (
        (rect.left + dx) > 0 &&
        (rect.left + dx + rect.width) < canvas.width
      ){
        rect.left += dx;
      }

      if (
        (rect.top + dy) > 0 &&
        (rect.top + dy + rect.height) < canvas.height
      ){
        rect.top += dy;
      }

      startX = mouseX;
      startY = mouseY;

  } else if (dragTL) {
      e.preventDefault();
      e.stopPropagation();

      var newSide =
        (
          Math.abs(rect.left + rect.width - mouseX) +
          Math.abs(rect.height + rect.top - mouseY)
        ) / 2;

      if (newSide > 150){
        rect.left = rect.left + rect.width - newSide;
        rect.top = rect.height + rect.top - newSide;
        rect.width = rect.height = newSide;
      }

  } else if (dragTR) {
      e.preventDefault();
      e.stopPropagation();

      var newSide =
        (
          Math.abs(mouseX - rect.left) +
          Math.abs(rect.height + rect.top - mouseY)
        ) / 2;

      if (newSide > 150){
          rect.top = rect.height + rect.top - newSide;
          rect.width = rect.height = newSide;
      }

  } else if (dragBL) {
      e.preventDefault();
      e.stopPropagation();

      var newSide =
        (
          Math.abs(rect.left + rect.width - mouseX) +
          Math.abs(rect.top - mouseY)
        ) / 2;

      if (newSide > 150)
      {
        rect.left = rect.left + rect.width - newSide;
        rect.width = rect.height = newSide;
      }

  } else if (dragBR) {
      e.preventDefault();
      e.stopPropagation();

      var newSide =
        (
          Math.abs(rect.left - mouseX) +
          Math.abs(rect.top - mouseY)
        ) / 2;

      if (newSide > 150)
      {
       rect.width = rect.height = newSide;
      }
  }

  drawRectInCanvas();
}

function updateCurrentCanvasRect(){
  current_canvas_rect.height = canvas.height
  current_canvas_rect.width = canvas.width
  current_canvas_rect.top = image.offsetTop
  current_canvas_rect.left = image.offsetLeft
}

function repositionCanvas(){

  console.log("image w and h ", image.height, image.width);

  canvas.height = image.height;
  canvas.width = image.width;

  canvas.style.top = image.offsetTop + "px";
  canvas.style.left = image.offsetLeft + "px";

  var ratio_w = canvas.width / current_canvas_rect.width;
  var ratio_h = canvas.height / current_canvas_rect.height;

  rect.top = rect.top * ratio_h;
  rect.left = rect.left * ratio_w;
  rect.height = rect.height * ratio_h;
  rect.width = rect.width * ratio_w;

  updateCurrentCanvasRect();
  drawRectInCanvas();
}

function initCanvas(image){
  canvas.height = image.height;
  canvas.width = image.width;

  canvas.style.top = image.offsetTop + "px";
  canvas.style.left = image.offsetLeft + "px";

  console.log("INITCANVAS");

  updateCurrentCanvasRect();
}



export function Init(
  imageElement: HTMLImageElement,
  canvasElement: HTMLCanvasElement
){

  console.log("image ", imageElement);
  console.log("image ", typeof(imageElement));

  console.log("canvas ", canvasElement);
  console.log("canvas ", typeof(canvasElement));

  image = imageElement;
  canvas = canvasElement;

  console.log("ASSIGNED IMAGE ", image);
  console.log("ASSIGNED CANVAS ", canvas);

  canvas.addEventListener('pointerdown', mouseDown, false);
  canvas.addEventListener('pointerup', mouseUp, false);
  canvas.addEventListener('pointermove', mouseMove, false);

  initCanvas(image);
  drawRectInCanvas();

  window.addEventListener('resize', repositionCanvas);

  return () => {
    canvas.removeEventListener('pointerdown', mouseDown, false);
    canvas.removeEventListener('pointerup', mouseUp, false);
    canvas.removeEventListener('pointermove', mouseMove, false);

    window.removeEventListener('resize', repositionCanvas);
  };
}