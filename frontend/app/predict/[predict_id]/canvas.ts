
let image: HTMLImageElement;
let canvas: HTMLCanvasElement;

var handleRadius = 5;
const deleteButtonRadius = handleRadius + 1;
const deleteButtonOffsetX = 20;
let choosen_clicked_index: number | null = null;
let choosen_classname_for_Rect: number | null = null;


var dragTL = false;
var dragBL = false;
var dragTR = false;
var dragBR = false;
var dragWholeRect = false;
var isDrawingNew = false;

var newRectAnchorX: number, newRectAnchorY: number;
var mouseX: number, mouseY: number;
var startX: number, startY: number;

let passed_sam_data = [];
let sam_prediction_happened_boolean = false;

interface RectShape {
  id: string;
  belongs_to_img: number;
  sam_inference: string;
  linked_with_sam_id: string;
  color: string;
  stroke_color: string;
  muted_color: string,
  muted_strokecolor: string,
  canvas_width: number,
  canvas_height: number,
  left: number;
  top: number;
  width: number;
  height: number;
}

let activeColorClassname: number[] | null = null;
let set_color_changes_once = false;

let rects: RectShape[] = [];

let activeIndex = -1;
let id_to_match_for_colorchange;
var current_canvas_rect: any = {};

let onRectsChange: ((rects: RectShape[]) => void) | null = null;

const MIN_SIZE = 20;

function notifyReact() {
  if (onRectsChange) onRectsChange(rects.map(r => ({ ...r })));
}

function makeId() {
  return `rect_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
}

export function belongs_to_index(clicked_index: number){
    console.log("BELONGS_TO_INDX")
    console.log("belongs_to_index gotten in canvas.ts", clicked_index);
    choosen_clicked_index = clicked_index;

    return choosen_clicked_index;
}


function drawCircle(x: number, y: number, radius: number, stroke_color) {
  var ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.fillStyle = stroke_color;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fill();
}

function drawHandles(r: RectShape) {
  drawCircle(r.left, r.top, handleRadius, r.stroke_color);
  drawCircle(r.left + r.width, r.top, handleRadius, r.stroke_color);
  drawCircle(r.left + r.width, r.top + r.height, handleRadius, r.stroke_color);
  drawCircle(r.left, r.top + r.height, handleRadius, r.stroke_color);
  const del = getDeleteButtonPos(r);
  drawDeleteButton(del.x, del.y, deleteButtonRadius);
}

function drawDeleteButton(x: number, y: number, deletebutton_radius: number) {
  var ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.fillStyle = "#c77777";
  ctx.beginPath();
  ctx.arc(x, y, deletebutton_radius, 0, 2 * Math.PI);
  ctx.fill();
}

function getDeleteButtonPos(r: RectShape) {
  return {
    x: r.left + r.width + deleteButtonOffsetX,
    y: r.top + r.height,
  };
}

function checkOnDeleteButton(x: number, y: number, r: RectShape) {
  const pos = getDeleteButtonPos(r);
  const dx = x - pos.x;
  const dy = y - pos.y;
  return Math.sqrt(dx * dx + dy * dy) < deleteButtonRadius + 6;
}

function deleteRect(index: number) {
  rects.splice(index, 1);
  activeIndex = -1;
  drawRectInCanvas();
  notifyReact();
}


export function passing_sam_data_to_canvas(sam_data){
    passed_sam_data = sam_data
    sam_prediction_happened_boolean = true
    //console.log("passing_sam_data_to_canvas is ", passed_sam_data)
    //console.log("sam_prediction_happened_boolean is ", sam_prediction_happened_boolean)
}

export function setActiveColorClassname(colors_classname: number[] | null, classname_for_Rect: number) {

  if (!canvas) {
    console.warn("setActiveColorClassname called before Init() — ignoring");
    return;
  }
  if (Array.isArray(colors_classname) && colors_classname.length === 4) {
    activeColorClassname = colors_classname;
    //console.log("color_classname in canvas.ts ", activeColorClassname)
  } else {
    activeColorClassname = null;
    //console.log("color_classname in canvas.ts ", activeColorClassname)
  }
  choosen_classname_for_Rect = classname_for_Rect;
    //console.log("that is classname ", classname_for_Rect);
    //console.log("used set modular in canvas.ts", choosen_classname_for_Rect);
  drawRectInCanvas();
}

function rgbaString(c: number[]): string {
  const [r, g, b, a] = c;
  return `rgba(${r}, ${g}, ${b}, ${a / 255})`;
}


function rgbaStringfor_lowered_opacity(c: number[]): string {
  const [r, g, b, a] = c;
  return `rgba(${r}, ${g}, ${b}, ${0.4})`;
}


function drawOneRect(r: RectShape, isActive: boolean) {
  var ctx = canvas.getContext("2d");
  if (!ctx) return;
  let idtomatchto = choosen_clicked_index;

  //console.log("r id is ", r.id)
  //console.log("clicked index ", idtomatchto)
  if (r.belongs_to_img != idtomatchto) return;

  ctx.beginPath();
  ctx.lineWidth = 2;
  //console.log("activeColorClassname is ", activeColorClassname)
  if(id_to_match_for_colorchange === r.id){
      //console.log("id matched!! ", r.id, id_to_match_for_colorchange)
  if(isDrawingNew != true && dragWholeRect === true && activeColorClassname != null){
    const asString_stroke_color = rgbaString(activeColorClassname);
    const asString_color = rgbaStringfor_lowered_opacity(activeColorClassname);
    r.color = asString_color;
    r.stroke_color = asString_stroke_color;
    //console.log("color and stroke_color ", r.color, r.stroke_color)
    //console.log("color changed, nulling it")
    r.muted_strokecolor = asString_color;
    r.classname = choosen_classname_for_Rect;
    activeColorClassname = null;

    }
  }
  ctx.fillStyle = isActive
    ? r.color
    : r.muted_color;
  ctx.strokeStyle = isActive ? r.stroke_color : r.muted_strokecolor;
  ctx.rect(r.left, r.top, r.width, r.height);
  ctx.fill();
  ctx.stroke();

  if (isActive) drawHandles(r);
}

function drawRectInCanvas() {
    //console.log("canvas in drawRectInCanvas" , canvas)
  var ctx = canvas.getContext("2d");
  if (!ctx) {
    console.error("Could not get canvas 2D context");
    return;
  }
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  rects.forEach((r, i) => drawOneRect(r, i === activeIndex));
}


function checkInRect(x: number, y: number, r: RectShape) {
  //console.log("click checking...")
  return x > r.left && x < r.width + r.left && y > r.top && y < r.top + r.height;
}

function checkCloseEnough(p1: number, p2: number) {
  return Math.abs(p1 - p2) < handleRadius + 6; // a little slack for touch/pointer precision
}

function getMousePos(canvasEl: HTMLCanvasElement, evt: any) {
  var clx, cly;
  if (evt.type == "touchstart" || evt.type == "touchmove") {
    clx = evt.touches[0].clientX;
    cly = evt.touches[0].clientY;
  } else {
    clx = evt.clientX;
    cly = evt.clientY;
  }
  var boundingRect = canvasEl.getBoundingClientRect();
  return { x: clx - boundingRect.left, y: cly - boundingRect.top };
}


function mouseDown(e: any) {
  var pos = getMousePos(canvas, e);
  mouseX = pos.x;
  mouseY = pos.y;

  if (activeIndex !== -1) {
    const r = rects[activeIndex];
    if (checkOnDeleteButton(mouseX, mouseY, r)) {
      deleteRect(activeIndex);
      return; // delete button clicked, skipping resize
    }
    if (checkCloseEnough(mouseX, r.left) && checkCloseEnough(mouseY, r.top)) {
      dragTL = true;
      drawRectInCanvas();
      return;
    }
    if (checkCloseEnough(mouseX, r.left + r.width) && checkCloseEnough(mouseY, r.top)) {
      dragTR = true;
      drawRectInCanvas();
      return;
    }
    if (checkCloseEnough(mouseX, r.left) && checkCloseEnough(mouseY, r.top + r.height)) {
      dragBL = true;
      drawRectInCanvas();
      return;
    }
    if (checkCloseEnough(mouseX, r.left + r.width) && checkCloseEnough(mouseY, r.top + r.height)) {
      dragBR = true;
      drawRectInCanvas();
      return;
    }
  }

  // checking if click happened inside of any neliöitä
  for (let i = rects.length - 1; i >= 0; i--) {
    if (checkInRect(mouseX, mouseY, rects[i])) {
      activeIndex = i;
      console.log("click happened inside of rect")
      console.log("activeIndex is", i)
      //console.log("all rects ", rects)
      console.log("id of click", rects[i].id)
      if (sam_prediction_happened_boolean == true){
              //console.log("rects[i].sam_inference",rects[i].sam_inference)
            rects[i].sam_inference = true
            //console.log("rects[i].sam_inference",rects[i].sam_inference)
            //console.log("all clicked sam data ", passed_sam_data)
            if(i <= passed_sam_data.length-1){
                //console.log("i is now ", i, "sam length is ", passed_sam_data.length-1)
              if(passed_sam_data[i].belongs_to_rect == rects[i].id){
                  //console.log("sam i id is ", passed_sam_data[i].belongs_to_rect)
                  //console.log("rects[i] id is ", rects[i].id)
                   console.log("before linked_with_sam_id?? ", rects[i].linked_with_sam_id)
                  if(rects[i].linked_with_sam_id == false){
                      rects[i].linked_with_sam_id = true;
                      console.log("after linked_with_sam_id?? ", rects[i].linked_with_sam_id)
                  } else {
                      rects[i].linked_with_sam_id=false;
                      console.log("after linked_with_sam_id?? ", rects[i].linked_with_sam_id)
                  }
              }
            }
        }
      id_to_match_for_colorchange = rects[i].id
      dragWholeRect = true;
      startX = mouseX;
      startY = mouseY;
      drawRectInCanvas();
      return;
    }
  }

  // start drawing a brand new rect, no clicks inside rectangulars happenend
  isDrawingNew = true;
  newRectAnchorX = mouseX;
  newRectAnchorY = mouseY;
  //makeId()

  const draft: RectShape = { id: makeId(), belongs_to_img: choosen_clicked_index,sam_inference: false, linked_with_sam_id: false, classname: null, color: "rgba(199, 87, 231, 0.25)", stroke_color: "#c757e7" , muted_color: "rgba(120, 120, 120, 0.15)", muted_strokecolor: "#999999",canvas_width: canvas.width, canvas_height: canvas.height,left: mouseX, top: mouseY, width: 0, height: 0 };
  rects.push(draft);
  activeIndex = rects.length - 1;

  drawRectInCanvas();
}

function mouseMove(e: any) {
  var pos = getMousePos(canvas, e);
  mouseX = pos.x;
  mouseY = pos.y;

  if (activeIndex === -1) return;
  const r = rects[activeIndex];

  if (isDrawingNew) {
    e.preventDefault();
    e.stopPropagation();

    r.left = Math.min(newRectAnchorX, mouseX);
    r.top = Math.min(newRectAnchorY, mouseY);
    r.width = Math.abs(mouseX - newRectAnchorX);
    r.height = Math.abs(mouseY - newRectAnchorY);
  } else if (dragWholeRect) {
    e.preventDefault();
    e.stopPropagation();
    var dx = mouseX - startX;
    var dy = mouseY - startY;
    if (r.left + dx > 0 && r.left + dx + r.width < canvas.width) r.left += dx;
    if (r.top + dy > 0 && r.top + dy + r.height < canvas.height) r.top += dy;
    startX = mouseX;
    startY = mouseY;
  } else if (dragTL) {
    e.preventDefault();
    e.stopPropagation();
    var newSide = (Math.abs(r.left + r.width - mouseX) + Math.abs(r.height + r.top - mouseY)) / 2;
    if (newSide > 20) {
      r.left = r.left + r.width - newSide;
      r.top = r.height + r.top - newSide;
      r.width = r.height = newSide;
    }
  } else if (dragTR) {
    e.preventDefault();
    e.stopPropagation();
    var newSide = (Math.abs(mouseX - r.left) + Math.abs(r.height + r.top - mouseY)) / 2;
    if (newSide > 20) {
      r.top = r.height + r.top - newSide;
      r.width = r.height = newSide;
    }
  } else if (dragBL) {
    e.preventDefault();
    e.stopPropagation();
    var newSide = (Math.abs(r.left + r.width - mouseX) + Math.abs(r.top - mouseY)) / 2;
    if (newSide > 20) {
      r.left = r.left + r.width - newSide;
      r.width = r.height = newSide;
    }
  } else if (dragBR) {
    e.preventDefault();
    e.stopPropagation();
    var newSide = (Math.abs(r.left - mouseX) + Math.abs(r.top - mouseY)) / 2;
    if (newSide > 20) {
      r.width = r.height = newSide;
    }
  }

  drawRectInCanvas();
}

function mouseUp(e: any) {
  if (isDrawingNew && activeIndex !== -1) {
    const r = rects[activeIndex];
    // unohdetaan pienet clicks koska they never would become a real box
    if (r.width < MIN_SIZE || r.height < MIN_SIZE) {
      rects.splice(activeIndex, 1);
      activeIndex = -1;
    }
  }

  dragTL = dragTR = dragBL = dragBR = false;
  dragWholeRect = false;
  isDrawingNew = false;

  drawRectInCanvas();
  notifyReact();
}


function updateCurrentCanvasRect() {
  current_canvas_rect.height = canvas.height;
  current_canvas_rect.width = canvas.width;
  current_canvas_rect.top = image.offsetTop;
  current_canvas_rect.left = image.offsetLeft;
}

function repositionCanvas() {
  canvas.height = image.height;
  canvas.width = image.width;
  canvas.style.top = image.offsetTop + "px";
  canvas.style.left = image.offsetLeft + "px";

  var ratio_w = canvas.width / current_canvas_rect.width;
  var ratio_h = canvas.height / current_canvas_rect.height;

  // re scaalataan kaikki neliöt ratiolla
  rects.forEach(r => {
    r.top *= ratio_h;
    r.left *= ratio_w;
    r.height *= ratio_h;
    r.width *= ratio_w;
  });

  updateCurrentCanvasRect();
  drawRectInCanvas();
  notifyReact();
}

function initCanvas(image: HTMLImageElement) {
  canvas.height = image.height;
  canvas.width = image.width;
  canvas.style.top = image.offsetTop + "px";
  canvas.style.left = image.offsetLeft + "px";
  //console.log("image ", image)
  //console.log("canvas ", canvas)
  console.log("typeof canvas_height and canvas_width", typeof(canvas.height), typeof(canvas.width))
  updateCurrentCanvasRect();
}

export function Init(
  imageElement: HTMLImageElement,
  canvasElement: HTMLCanvasElement,
  onChange?: (rects: RectShape[]) => void
) {
  image = imageElement;
  canvas = canvasElement;
  onRectsChange = onChange ?? null;


  canvas.addEventListener("pointerdown", mouseDown, false);
  canvas.addEventListener("pointerup", mouseUp, false);
  canvas.addEventListener("pointermove", mouseMove, false);

  initCanvas(image);
  //drawRectInCanvas();

  window.addEventListener("resize", repositionCanvas);

  return () => {
    canvas.removeEventListener("pointerdown", mouseDown, false);
    canvas.removeEventListener("pointerup", mouseUp, false);
    canvas.removeEventListener("pointermove", mouseMove, false);
    window.removeEventListener("resize", repositionCanvas);
  };
}

export function getRects(): RectShape[] {
  return rects.map(r => ({ ...r }));
}