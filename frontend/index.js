let visual = null
let hotText = {}
let labels = {}
let darkurl = ""
let lighturl = ""

function init() {
    visual = new Visual()
    let renderer = new Renderer(geometry, visual)
    
    labels = makeLabels(geometry)

    colorText(geometry)

    document.addEventListener( 'keydown', onKeyDown(renderer))
    document.addEventListener('touchstart', () => renderer.render())
    document.addEventListener('touchmove', () => renderer.render())
    let textElements = Array.from(document.getElementsByClassName('GeoElement'))
    textElements.forEach(
	(el) => {
	    el.addEventListener('mouseenter', overTextChange(renderer))
	    el.addEventListener('mouseleave', overTextRevert(renderer))
	    el.addEventListener('touchstart', textToggle(renderer))
	})
    document.getElementById("themeswitch").onclick = themeSwitch(renderer)

    setStyleURLs()
    
    renderer.render()
}

function sortItems(toDraw, objs) {
    sorted = []
    // Gonna do 4 passes, first gets circles and polys,
    // then everything that isn't a point
    // then all the items that are 'textHot'
    // then the points

    toDraw.forEach((id) => {
	if((objs[id].type == "Polygon" || objs[id].type == "Circle") && isHot(objs[id])) {
	    sorted.push(id)
	}
    })

    toDraw.forEach((id) => {
	if((objs[id].type == "Polygon" || objs[id].type == "Circle") && !isHot(objs[id])) {
	    sorted.push(id)
	}
    })
    
    toDraw.forEach((id) => {
	if(objs[id].type == "Line" && !isHot(objs[id])) {
	    sorted.push(id)
	}
    })

    
    toDraw.forEach((id) => {
	if(isHot(objs[id]) && objs[id].type != "Polygon" && objs[id].type != "Circle") {
	    sorted.push(id)
	}
    })

    toDraw.forEach((id) => {
	if(objs[id].type == "Point") {
	    sorted.push(id)
	}
    })

    

    return sorted
}

class Renderer {
    constructor(geometry, visual) {
	this.geo = geometry
	this.visual = visual
	this.anim_index = 0
	this.makeRenderFuncs()
	if(geometry.animations.length > 1)
	    this.createStepButtons()

	window.addEventListener("mousemove", (e) => {
	    if(this.visual.mouseInCanvas) {
		this.render()
	    }
	})
	this.updateAnimation(0)
    }

    makeRenderFuncs() {
	let visual = this.visual
	this.renderFuncs = []
	for(let step = 0; step < this.geo.animations.length; step++) {
	    let toDraw = geometry.animations[step]
	    let objects = this.geo.geometry
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
	    let render =  function() {
		visual.clear()
		let toDrawSorted = sortItems(toDraw, objects)
		for(let i = 0; i < toDrawSorted.length; i++) {
		    let id = toDrawSorted[i]
		    let geo = objects[id]
		    let textHot = isHot(geo)
		    let color = textHot ? visual.hotColor : objects[id].color
		    let hot = false

		    switch(geo.type) {
		    case "Point":
			hot = visual.drawPoint(geo.id, geo.data, color)
			highlightText(geo, hot, textHot, true)
			break;
		    case "Line":
			hot = visual.drawLine(geo.id,
					      objects[geo.data.p1].data,
					      objects[geo.data.p2].data,
					      color)

			highlightText(geo, hot, textHot)
			break;
		    case "Circle":
			hot = visual.drawCircle(geo.id, geo.data.center, geo.data.radius, objects[id].color, textHot, objects[id].color)
			highlightText(geo, hot, textHot)
			break;
		    case "Polygon":
			hot = visual.drawPoly(geo.id, geo.data.points.map((p) => objects[p].data), objects[id].color, textHot)
			highlightText(geo, hot, textHot)
			break;
		    default:
			console.log("We don't handle type " + geo.type)
		    }
		}
	    }

	    this.renderFuncs.push(render)
	}
    }

    render() {
	this.renderFuncs[this.anim_index]()
    }

    createStepButtons() {
	let visual = this.visual
	let next = document.createElement('input')
	let prev = document.createElement('input')

	next.className = 'step_btn'
	next.id = 'next_step'
	next.value = 'Next Step'
	next.type = 'button'
	prev.className = 'step_btn'
	prev.id = 'prev_step'
	prev.value = 'Prev Step'
	prev.type = 'button'
	
	next.onclick = () => {
	    this.updateAnimation(+1)
	}
	prev.onclick = () => {
	    this.updateAnimation(-1)
	}

	document.body.append(prev)
	document.body.append(next)

	let width = -1 // Only respond to real 'resize' events
	let moveButtons = () => {
	    if(window.innerWidth == width) {
		return
	    }
	    else {
		width = window.innerWidth
	    }
	    let rect = visual.canvasRect
	    let pad = 40

	    prev.style.left = rect.left + pad + 'px'
	    prev.style.top = rect.bottom - prev.clientHeight - pad + 'px'
	    next.style.left  = rect.right - next.clientWidth - pad + 'px'
	    next.style.top = rect.bottom - next.clientHeight - pad + 'px'
	}
	moveButtons()

	window.addEventListener('resize', moveButtons)
    }

    updateAnimation(delta) {
	clearText(this.geo, this.anim_index)
	
	if(delta < 0) {
	    this.anim_index = this.anim_index === 0 ? this.anim_index : this.anim_index + delta
	}
	else if(delta > 0) {
	    this.anim_index = this.anim_index === geometry.animations.length-1 ? this.anim_index : this.anim_index + delta
	}

	let prev = Array.from(document.getElementsByClassName('step_highlighted'))
	prev.forEach((el) => el.className = '')
	

	let par = document.getElementById('step_' + this.anim_index)
	if(par) {
	    par.className = 'step_highlighted'
	}

	this.render()
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

function highlightText(geo, isHot, textHot, isPoint) {
    isHot = isHot || textHot
    if(textHot || isPoint) {
	showLabel(geo.id)
    }
    else {
	hideLabel(geo.id)
    }
    let elements = document.getElementsByName("text_"+geo.type.toLowerCase()+"_"+geo.id)
    elements.forEach((el) => {
	el.style.color = getHex(geo.color)
	if(isHot) {
	    el.classList.add('shadowed')
	}
	else {
	    el.classList.remove('shadowed')
	}
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
	    default:
		continue
	    }
	    x = ( x + 1) / 2 + 0.012
	    y = (-y + 1) / 2 - 0.03
	    elem.style.left = (Math.floor(x * visual.size) + visual.canvasRect.left) + 'px'
	    elem.style.top = (Math.floor(y * visual.size) + visual.canvasRect.top) + 'px'
	    labels[obj.id] = elem
	    let width = window.innerWidth // Workaround for safari resize bug
	    window.addEventListener('resize', function() {
		if(window.innerWidth === width) {
		    return
		}
		else {
		    width = window.innerWidth
		}
		let x = obj.data.x
		let y = obj.data.y
		let l = elem
		x = ( x + 1) / 2 + 0.012
		y = (-y + 1) / 2 - 0.03
		l.style.left = (Math.floor(x * visual.size) + visual.canvasRect.left) + 'px'
		l.style.top = (Math.floor(y * visual.size) + visual.canvasRect.top) + 'px'
	    })
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

function clearText(geometry, step) {
    geometry.animations[step].forEach((id) => {
	highlightText(geometry.geometry[id], false, false)
    })
}

function colorText(geometry) {
    geometry.animations.forEach((step) => {
	step.forEach((id) => highlightText(geometry.geometry[id], false, false))
    })
}




/*
  All Event Callbacks
*/

/* Two functions for hovering over span elements, and leaving from hover */
function overTextChange(renderer)  {
    return (event) => {
	event.preventDefault()
	let obj_id_str = event.target.getAttribute("name").replace('text_', '');
	hotText[obj_id_str] = true
	renderer.render()
    }
}

function overTextRevert(renderer)  {
    return () => {
	let obj_id_str = event.target.getAttribute("name").replace('text_', '');
	hotText[obj_id_str] = false
	renderer.render()
    }
}

function textToggle(renderer)  {
    return (event) => {
	event.preventDefault()
	let obj_id_str = event.target.getAttribute("name").replace('text_', '');
	hotText[obj_id_str] = hotText[obj_id_str] ? false : true
	renderer.render()
    }
}

function onKeyDown( r ) {
    return () => {
	if(event.keyCode == 37) {
	    r.updateAnimation(-1)
	}
	else if(event.keyCode == 39) {
	    r.updateAnimation(+1)
	}
    }
}

function themeSwitch(renderer) {
    return () => {
	let style = document.getElementById("stylesheet")
	let check = document.getElementById("themeswitch")

	if(check.checked) {
	    style.href = lighturl
	    visual.light = true
	}
	else {
	    style.href = darkurl
	    visual.light = false
	}
	renderer.render()
    }
}

function setStyleURLs() {
    let style = document.getElementById("stylesheet")

    darkurl = style.href
    lighturl = darkurl.replace("default.css", "light.css")
    console.log(darkurl)
    console.log(lighturl)
}

