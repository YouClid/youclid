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
	    if(!obj.data.center || !obj.data.radius) {
		let circle = circleFromPoints(objects[obj.data.p1].data,
					      objects[obj.data.p2].data,
					      objects[obj.data.p3].data)
		obj.data.center = circle.center
		obj.data.radius = circle.radius
	    }
	    else {
		obj.data.center = objects[obj.data.center].data
	    }
	}
    }
    
    return function(visual) {
	for(let i = 0; i < toDraw.length; i++) {
	    let id = toDraw[i]
	    let geo = objects[id]
	    let red = [1.0, 0.0, 0.0, 1.0]

	    switch(geo.type) {
	    case "Point":
		visual.drawPoint(geo.id, geo.data, red)
		break;
	    case "Line":
		visual.drawLine(geo.id,
				objects[geo.data.p1].data,
				objects[geo.data.p2].data,
				red)
		break;
	    case "Circle":
		visual.drawCircle(geo.id, geo.data.center, geo.data.radius, red)
		break;
	    case "Polygon":
		visual.drawPolygon(geo.id, geo.points.map((p) => objects[p].data), red)
		break;
	    default:
		console.log("We don't handle type " + geo.type)
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


function onMouseDown( event ) {
    event.preventDefault();
    mouse.x = ( event.clientX / size ) * 2 - 1;
    mouse.y = - ( event.clientY / size ) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );
    let intersects = raycaster.intersectObjects(scene.children);
    if ( intersects.length > 0 ) {
	current = intersects[0]
	oldPos = current.point.clone()
	originalCenter = current.object.position.clone()
	// originalCenter = current.object.geometry.vertices[0].clone()
    }
}

let changed = {text:[], objects:[]}
let objectColors = {}

function onMouseMove( event ) {
    let xgood = event.clientX > canvasRect.left && event.clientX < canvasRect.right
    let ygood = event.clientY > canvasRect.top  && event.clientY < canvasRect.bottom
    let text = []
    let objects = []

    if(xgood && ygood) {
	mouse.x = ((event.clientX - canvasRect.left) / size ) * 2 - 1;
	mouse.y = - ( (event.clientY - canvasRect.top) / size ) * 2 + 1;
	raycaster.setFromCamera( mouse, camera );
	let intersects = raycaster.intersectObjects(scene.children);
	for(let i = 0; i<intersects.length; i++) {
	    let curr = intersects[i].object
	    let oldColor = new THREE.Color(curr.material.color)
	    if(!objectColors[curr.uuid]) {
		objectColors[curr.uuid] = oldColor
	    }
	    objects.push(curr)
            let idStr = curr.name.replace('object', 'text');
	    let elements = document.getElementsByName(idStr)
	    elements.forEach((element) => {
		text.push(element)
	    })
		
	    
	}

    }

    changed.text.forEach((c) => c.style.backgroundColor = "#dddddd")
    changed.objects.forEach((c) => c.material.color.setHex(objectColors[c.uuid].getHex()))

    text.forEach((c) => c.style.backgroundColor = "yellow")
    objects.forEach((c) => c.material.color.setHex( 0xfffa00 ))

    changed.text = text
    changed.objects = objects
}

function onMouseUp( event ) {
    current = null;
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
    if(event.keyCode == 37) {
	anim_index = anim_index === 0 ? anim_index : anim_index - 1
	visual.setRender(makeRender(geometry, anim_index))
    }
    else if(event.keyCode == 39) {
	anim_index = anim_index === geometry.animations.length-1 ? anim_index : anim_index + 1
	visual.setRender(makeRender(geometry, anim_index))
    }
}
