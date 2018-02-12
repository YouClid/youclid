let anim_index = 0
let visual = null

function init() {
    let render = makeRender(geometry, anim_index)

    visual = new Visual(render)

    document.addEventListener( 'keydown', onKeyDown)
}

function makeRender(geometry, step) {
    let toDraw = geometry.animations[step]
    let objects = geometry.geometry
    for(let key in objects) {
        let obj = objects[key]
        if(obj.type === "Circle") {
            if(!obj.data.center && !obj.data.radius) {
            let circle = circleFromPoints(objects[obj.data.p1].data,
                              objects[obj.data.p2].data,
                              objects[obj.data.p3].data)
            obj.data.center = circle.center
            obj.data.radius = circle.radius
            }
            else if (!obj.data.radius && obj.data.center) {
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
    return function(visual) {
	for(let i = 0; i < toDraw.length; i++) {
	    let id = toDraw[i]
	    let geo = objects[id]
	    let color = objects[id].color
	    let hot = false

	    switch(geo.type) {
	    case "Point":
		break;
	    case "Line":
		hot = visual.drawLine(geo.id,
					  objects[geo.data.p1].data,
					  objects[geo.data.p2].data,
					  color)

		highlightText(geo, hot)
		break;
	    case "Circle":
		hot = visual.drawCircle(geo.id, geo.data.center, geo.data.radius, color)
		highlightText(geo, hot)
		break;
	    case "Polygon":
		hot = visual.drawPoly(geo.id, geo.data.points.map((p) => objects[p].data), color)
		highlightText(geo, hot)
		break;
	    default:
		console.log("We don't handle type " + geo.type)
	    }
	}
	
	// Draw points last
	for(let i = 0; i < toDraw.length; i++) {
	    let id = toDraw[i]
	    let geo = objects[id]
	    let color = objects[id].color
	    let hot = false

	    if(geo.type === "Point") {
		hot = visual.drawPoint(geo.id, geo.data, color)
		highlightText(geo, hot)
	    }
	}
    }
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

function circleFromPoints(p1, p2, p3) {
    let m1 = (p1.y-p2.y)/(p1.x-p2.x)
    let m2 = (p3.y-p2.y)/(p3.x-p2.x)

    let ma = -1.0*(1.0/m1)
    let mb = -1.0*(1.0/m2)

    let xa = 0.5*(p1.x+p2.x)
    let ya = 0.5*(p1.y+p2.y)
    let xb = 0.5*(p2.x+p3.x)
    let yb = 0.5*(p2.y+p3.y)

    let center = {x:0, y:0}
    center.x = ((ma*xa)-(mb*xb)+yb-ya)/(ma-mb)
    center.y = (mb*(center.x-xb))+yb

    let radius = dist(center, p1)

    return {center: center, radius: radius}
}

function highlightText(geo, isHot) {
    let elements = document.getElementsByName("text_"+geo.type.toLowerCase()+"_"+geo.id)
    elements.forEach((el) => {
    console.log(el.classList[1])
    if(isHot){
        el.style.backgroundColor = 'yellow'
    }
    else if(el.classList[1] <= "step_"+anim_index){
        el.style.backgroundColor = getHex(geo.color)
    }
    else{
        el.style.backgroundColor = '#5A5A5A'
    }
	el.style.color = geo.color.reduce((x,y) => x+y) <= 1.8 && !isHot ? 'white' : '#0f0f0f'
    })
}

function clearText(){
    let elements = document.getElementsByClassName("GeoElement")
    for (var el of elements) {
        el.style.backgroundColor = '#5A5A5A'
    }

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
    


/*
  All Event Callbacks
*/

/* Two functions for hovering over span elements, and leaving from hover */
function overTextChange(event)  {
    if(event.target.tagName === "SPAN") {
        event.target.style.backgroundColor = "yellow";
        let obj_id_str = event.target.getAttribute("name").replace('text', 'object');
        //alert(obj_id_str);
        testname = scene.getObjectByName(obj_id_str);
        //alert(testname.name);
        if(testname != null){
          oldcolor = new THREE.Color( testname.material.color );
          testname.material.color.setHex( 0xfffa00 );
      }
    }
}

function overTextRevert(event)  {
    if(event.target.tagName === "SPAN") {
        event.target.style.backgroundColor = "#dddddd";
        if(testname != null){
          testname.material.color.setHex( oldcolor.getHex() );
      }
        oldcolor=null;
        testname=null;
   }
}


function onTouchStart( event ) {
    event.preventDefault();
    event.clientX = event.touches[0].clientX;
    event.clientY = event.touches[0].clientY;
    onMouseDown( event );
}

function onTouchMove( event ) {
    event.preventDefault();
    event.clientX = event.touches[0].clientX;
    event.clientY = event.touches[0].clientY;
    onMouseMove( event );
}

function onTouchEnd( event ) {
    event.preventDefault();
    onMouseUp( event );
}

function onKeyDown( event ) {
    clearText()
    if(event.keyCode == 37) {
	anim_index = anim_index === 0 ? anim_index : anim_index - 1
	visual.setRender(makeRender(geometry, anim_index))
    }
    else if(event.keyCode == 39) {
	anim_index = anim_index === geometry.animations.length-1 ? anim_index : anim_index + 1
	visual.setRender(makeRender(geometry, anim_index))
    }
}
