
//current default size for svg
var xAx = 800;
var yAx = 800;


function init(){
  displaySVG();
}
function displaySVG() {
/*
  var div1 = document.createElement('div1');
  div1.id = "div1";
  document.body.appendChild(div1);
*/
    var img = SVG('text');
    //var img = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    img.size(xAx, yAx);
    //createImage(img);
    makeSVG(img, geometry);

}

function makeSVG(image, geometry) {
    //let toDraw = geometry.animations[step]
    let objects = geometry.geometry
    for(let ckey in objects) {
      let obj = objects[ckey]
      if(obj.type === "Circle") {
  /*        if(!obj.data.center && !obj.data.radius) {
          let circle = circleFromPoints(objects[obj.data.p1].data,
                            objects[obj.data.p2].data,
                            objects[obj.data.p3].data)
          obj.data.center = circle.center
          obj.data.radius = circle.radius
          }
          else*/ if (!obj.data.radius && obj.data.center) {
              // Get the coordinates of a point on the circle
              let otherPoint = objects[obj.data.p1].data
              // Get the coordinates of the center of the circle
              let center = objects[obj.data.center].data
              // Compute the distance from the center to a point (the radius)
              obj.data.radius = dist(center, otherPoint)
              // Update the center of the circle to be the coordinates of
              // the center
              obj.data.center = center
          }
        // The center is given as a point (something like "A")
          else if(typeof(obj.data.center) === 'string') {
              obj.data.center = objects[obj.data.center].data
          }
        }
      }

    for(let key in objects) {
        let geo = objects[key]
        colorText(geo);
        switch(geo.type) {
          case "Point":
            break;
          case "Line":
            drawLine(image, geo.id, objects[geo.data.p1].data, objects[geo.data.p2].data, geo.color)
            break;
          case "Circle":
            drawCircle(image, geo.id, geo.data.center, geo.data.radius, geo.color)
            break;
          case "Polygon":
            drawPoly(image, geo.id, geo.data.points.map((p) => objects[p].data), geo.color)
            break;
          default:
            console.log("We don't handle type " + geo.type)
          }
      }

      // Draw points last
      for(let key in objects) {
          let geo = objects[key];
            if(geo.type === "Point") {
              drawPoint(image, geo.id, geo.data, geo.color)
            }

      }

  }

function drawLine(image, id, pt1, pt2, color){
    let x1 = coordToImageX(pt1.x);
    let y1 = coordToImageY(pt1.y);
    let x2 = coordToImageX(pt2.x);
    let y2 = coordToImageY(pt2.y);

    image.line(x1, y1, x2, y2).stroke({ color: getHex(color), opacity: getOpacity(color), width: 1});
}

function drawCircle(image, id, center, radius, color){
    let cx = coordToImageX(center.x);
    let cy = coordToImageY(center.y);
    let diam = distToImage(radius)*2;


    image.circle(diam).cx(cx).cy(cy).fill('none').stroke({color : getHex(color), opacity: getOpacity(color), width: 1 });
}

function drawPoly(image, id, points, color){

  let arr = [];
  for(let item in points){
    let pnt = points[item];
    arr[item] = [coordToImageX(pnt.x), coordToImageY(pnt.y)];
  }
    image.polygon(arr).fill('none').stroke({ color: getHex(color), opacity: getOpacity(color), width: 1});
}

function drawPoint(image, id, center, color){
    let cx = coordToImageX(center.x);
    let cy = coordToImageY(center.y);
    let diam = 5;


    image.circle(diam).cx(cx).cy(cy).fill(getHex(color)).stroke({color : getHex(color), opacity: getOpacity(color), width: 1 });

}

function coordToImageX(coord){
    return ((1 + coord) * (Math.min(xAx, yAx)/2));
}
function coordToImageY(coord){
    return ((1 - coord) * (Math.min(xAx, yAx)/2));
}
function distToImage(coord){
    return (coord * (Math.min(xAx, yAx)/2));
}


//Joe code = best code
function colorText(geo) {
    let elements = document.getElementsByName("text_"+geo.type.toLowerCase()+"_"+geo.id)
    elements.forEach((el) => {
	el.style.color = getHex(geo.color)
    })
}

function getHex(colorArr) {
    let color = '#'
    for(let i = 0; i<colorArr.length-1; i++) {
	let val =  Math.floor(255*colorArr[i]).toString(16)
	while(val.length < 2) {
	    val = '0' + val
	}
	color += val
    }
    return color
}

function getOpacity(colorArr){
  let len=colorArr.length;
  let opac = colorArr[len-1];
  return opac;
}

function dist(p1, p2) {
    if(p1.z && p2.z) {
	let xs, ys, zs
	xs = (p1.x-p2.x)*(p1.x-p2.x)
	ys = (p1.y-p2.y)*(p1.y-p2.y)
	zs = (p1.z-p2.z)*(p1.z-p2.z)
	return Math.sqrt(xs+ys+zs)
    } else {
	return Math.sqrt((p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y))
    }
}
