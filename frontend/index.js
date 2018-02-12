let anim_index = 0
let visual = null
let hotText = {}
let labels = {}

function init() {
    let render = makeRender(geometry, anim_index)
    
    visual = new Visual(render)
    
    labels = makeLabels(geometry)

    document.addEventListener( 'keydown', onKeyDown)
    let textElements = Array.from(document.getElementsByClassName('GeoElement'))
    textElements.forEach(
	(el) => {
	    el.addEventListener('mouseenter', overTextChange)
	    el.addEventListener('mouseleave', overTextRevert)
	})
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
	    let textHot = isHot(geo)
	    let color = textHot ? [1.0, 1.0, 0, 1.0] : objects[id].color
	    let hot = false

	    switch(geo.type) {
	    case "Point":
		break;
	    case "Line":
		hot = visual.drawLine(geo.id,
					  objects[geo.data.p1].data,
					  objects[geo.data.p2].data,
					  color)

		highlightText(geo, hot, textHot)
		break;
	    case "Circle":
		hot = visual.drawCircle(geo.id, geo.data.center, geo.data.radius, color)
		highlightText(geo, hot, textHot)
		break;
	    case "Polygon":
		hot = visual.drawPoly(geo.id, geo.data.points.map((p) => objects[p].data), color)
		highlightText(geo, hot, textHot)
		break;
	    default:
		console.log("We don't handle type " + geo.type)
	    }
	}
	
	// Draw points last
	for(let i = 0; i < toDraw.length; i++) {
	    let id = toDraw[i]
	    let geo = objects[id]
	    let textHot = isHot(geo)
	    let color = textHot ? [1.0, 1.0, 0, 1.0] : objects[id].color
	    let hot = false

	    if(geo.type === "Point") {
		hot = visual.drawPoint(geo.id, geo.data, color)
		highlightText(geo, hot, textHot)
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

function highlightText(geo, isHot, textHot) {
    isHot = isHot || textHot
    if(textHot) {
	showLabel(geo.id)
    }
    else {
	hideLabel(geo.id)
    }
    let elements = document.getElementsByName("text_"+geo.type.toLowerCase()+"_"+geo.id)
    elements.forEach((el) => {
	el.style.color = isHot ? 'yellow' : getHex(geo.color)
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

function isHot(geo) {
    return hotText[geo.type.toLowerCase()+"_"+geo.id] ? true : false
}


function makeLabels(data) {
    let geometry = data.geometry
    let anims = data.animations
    for(let i = 0; i<anims.length; i++) {
	for(let j = 0; j<anims[i].length; j++) {
	    let obj = geometry[anims[i][j]]
	    if(labels[obj.id]) continue
	    let elem = document.createElement('div')
	    elem.id = obj.id
	    elem.innerHTML = obj.id
	    elem.style.position = 'absolute'
	    elem.className = 'label'
	    elem.style.display = "none"
	    let x = 0
	    let y = 0
	    let point = null
	    switch(obj.type) {
	    case "Point":
		x = obj.data.x
		y = obj.data.y
		break;
	    case "Line":
		point = geometry[obj.data.p2].data
		x = point.x
		y = point.y
		break;
	    case "Circle":
		x = obj.data.center.x
		y = obj.data.center.y
		break;
	    case "Polygon":
		point = geometry[obj.data.points[0]].data
		x = point.x
		y = point.y
		break;
	    default:
		console.log("Can't make label for type " + obj.type)
	    }
	    x = ( x + 1) / 2 + 0.01
	    y = (-y + 1) / 2 - 0.025
	    elem.style.left = (Math.floor(x * visual.size) + visual.canvasRect.left) + 'px'
	    elem.style.top = (Math.floor(y * visual.size) + visual.canvasRect.top) + 'px'
	    labels[obj.id] = elem
	    document.body.appendChild(elem)
	}
    }
}

function showLabel(id) {
    let el = document.getElementById(id)
    if(el) el.style.display = "initial"
}

function hideLabel(id) {
    let el = document.getElementById(id)
    if(el) el.style.display = "none"
}
    


/*
  All Event Callbacks
*/

/* Two functions for hovering over span elements, and leaving from hover */
function overTextChange(event)  {
    let obj_id_str = event.target.getAttribute("name").replace('text_', '');
    hotText[obj_id_str] = true
    visual.update()
}

function overTextRevert(event)  {
    let obj_id_str = event.target.getAttribute("name").replace('text_', '');
    hotText[obj_id_str] = false
    visual.update()
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
