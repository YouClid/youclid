const vertexShader = `
precision mediump float;
attribute vec4 a_Position;
attribute vec4 a_Color;
varying vec4 v_Color;
void main() {
     gl_Position = a_Position;
     gl_PointSize = 10.0;
     v_Color = a_Color;
}
`

const fragmentShader = `
precision mediump float;
varying vec4 v_Color;
void main() {
     gl_FragColor = v_Color;
}
`


class Visual {
    constructor() {
	this.mouse = {x:1000, y:10000}
	this.mousedown = false
	this.mouseup = true

	this.gl = null
	this.glData = null

	let width = document.body.clientWidth
	this.mobile = width < 600
	
	width = this.mobile ? width : width*0.65
	this.size = Math.min(width, window.innerHeight)

	this.canvasRect = null

	this.mouseDown = false
	this.lineWidth = this.mobile ? 0.025 : 0.01

	this.light = false
	this.hotColor = [1.0, 1.0, 0, 1.0]
	
	this.init()
    }
    
    init() {
	
	
	let canvas = document.createElement('canvas')
	document.body.insertBefore(canvas, document.body.childNodes[2])

	// Adjust canvas size based on screen
	{
	    canvas.style.width = this.size + "px";
	    canvas.style.height = this.size + "px";

	    // set the size of the drawingBuffer
	    var devicePixelRatio = window.devicePixelRatio || 1;
	    canvas.width = this.size * devicePixelRatio;
	    canvas.height = this.size * devicePixelRatio;
	}

	let gl = canvas.getContext('webgl')
	
	let program = this.initShaders(gl, vertexShader, fragmentShader)
	gl.program = program
	gl.useProgram(program)
	
	let buf = gl.createBuffer()
	gl.bindBuffer(gl.ARRAY_BUFFER, buf)
	this.glData = new Float32Array(1024)

	this.gl = gl
	this.canvasRect = canvas.getBoundingClientRect()

	gl.lineWidth(4.0)

	// Register listeners
	document.addEventListener( 'mousemove', onMouseMove.bind(this));
	let touchevent = (e) => {
	    e.preventDefault();
	    event.clientX = event.touches[0].clientX;
	    event.clientY = event.touches[0].clientY;
	    let move = onMouseMove.bind(this)
	    move(e);
	}
	document.addEventListener( 'touchstart', touchevent);
	document.addEventListener( 'touchmove', touchevent);
	document.addEventListener( 'mousedown', () => this.mouseDown = true)
	document.addEventListener( 'mouseup', () => this.mouseDown = false)
	window.addEventListener( 'resize', onResize.bind(this));

    }

    clear() {
	let gl = this.gl
	if(this.light){
	    let bg = 1.0
	    gl.clearColor(bg, bg, bg, 1.0)
	    this.hotColor = [0.9, 0.9, 0.2, 1.0]
	}
	else {
	    gl.clearColor(0.0, 0.0, 0.0, 1.0)
	    this.hotColor = [1.0, 1.0, 0, 1.0]
	}
	gl.clear(gl.COLOR_BUFFER_BIT)
    }
    
    isHot(name) {
	let hot = this.hot[name]
	return hot ? true : false
    }

    initShaders(gl, vertSrc, fragSrc) {
	let vshader = gl.createShader(gl.VERTEX_SHADER)
	let fshader = gl.createShader(gl.FRAGMENT_SHADER)

	gl.shaderSource(vshader, vertSrc)
	gl.shaderSource(fshader, fragSrc)

	gl.compileShader(vshader)
	gl.compileShader(fshader)


	if (!gl.getShaderParameter(vshader, gl.COMPILE_STATUS)) {
	    alert('An error occurred compiling the shaders: ' + gl.getShaderInfoLog(vshader));
	    return null;
	}
	if (!gl.getShaderParameter(fshader, gl.COMPILE_STATUS)) {
	    alert('An error occurred compiling the shaders: ' + gl.getShaderInfoLog(fshader));
	    return null;
	}


	const shaderProgram = gl.createProgram();
	gl.attachShader(shaderProgram, vshader);
	gl.attachShader(shaderProgram, fshader);
	gl.linkProgram(shaderProgram);
	
	var success = gl.getProgramParameter(shaderProgram, gl.LINK_STATUS);
	if (!success) {
	    // something went wrong with the link
	    throw ("program filed to link:" + gl.getProgramInfoLog (shaderProgram));
	}
	
	return shaderProgram
    }


    dist(p1, p2) {
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

    pointUnderMouse(point) {
	let sz = 5.0/(2*this.size)
	let center = {x:point.x+(sz/2), y:point.y+(sz/2)}
	return this.dist(this.mouse, center) < 0.05
    }

    lineUnderMouse(p0, p1) {
	let mouse = this.mouse
	let n = sub(p1, p0)
	let a = p0
	let a_to_m = sub(mouse, a)
	let coeff = dot(n, a_to_m)/normsq(n)
	if(coeff < 0 || coeff > 1) {
	    return false
	}
	let d = this.dist(a_to_m, scale(n, coeff))
	let thresh = this.mobile ? 0.1 : 0.03
	return d < thresh
    }

    polyUnderMouse(points) {
	if(points.length < 2) {
	    return false
	}
	for(let i = 0; i<points.length; i++) {
	    let next = (i+1)%points.length
	    let p0 = points[i]
	    let p1 = points[next]
	    if(this.lineUnderMouse(p0, p1)) {
		return true
	    }
	}
	return false
    }



    flatten(arr) {
	return [].concat.apply([], arr);
    }

    /*************************************

         Drawing Primitives

    *************************************/


    drawPoint(ident, point, color) {
        // create a circular point (filled in) of radius 0.0125
	if(this.pointUnderMouse(point)) {
	    color = this.hotColor
	}
	let strokeColor = [0,0,0,1]
	let radius = this.mobile ? 0.025 : 0.013
        return this.drawCircle(ident, point, radius, strokeColor, true, color, 0.001)
    }


    makeLineBuf(points, color, width) {

	let vertices = []

	for(let i=0; i<points.length; i++) {
	    let p1 = points[i]
	    let p2 = i < points.length - 1 ? points[i+1] : points[i-1]
	    let n = i < points.length - 1 ? normal(sub(p1, p2)) : normal(sub(p2, p1))
	
	    let v1 = [
		p1.x + (width / 2 * n.x),
		p1.y + (width / 2 * n.y),
		0.0,
		1.0
	    ]
	    v1 = v1.concat(color)
	
	    let v2 = [
		p1.x - (width / 2 * n.x),
		p1.y - (width / 2 * n.y),
		0.0,
		1.0
	    ]
	    v2 = v2.concat(color)

	    vertices = vertices.concat(v1).concat(v2)
	}

	return vertices
    }

    drawLine(ident, p1, p2, color, changeOnHot=true) {

	let name = "object_line_" + ident.toString()

	let hot = false
	let active = false
    
	if(this.lineUnderMouse(p1, p2)) {
	    hot = true
	    if(this.mouseDown) {
		active = true
	    }
	}
    
	if(hot && changeOnHot) {
	    color = this.hotColor
	}

    
	let gl = this.gl
    
	let data = this.glData

	let FSIZE = data.BYTES_PER_ELEMENT

	let width = this.lineWidth
	let vertices = this.makeLineBuf([p1, p2], color, width)	
    
	data.set(vertices)

	gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
	let a_Position = gl.getAttribLocation(gl.program, "a_Position")
	gl.enableVertexAttribArray(a_Position)
	gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

	let a_Color = gl.getAttribLocation(gl.program, "a_Color")
	gl.enableVertexAttribArray(a_Color)
	gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)

	gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)

	return hot

    }

    getPoints(center, radius) {
	let points = []
	let theta = 0
	let inc = 0.05
	let tau = 2*Math.PI
	while(theta <= tau) {
	    let x = radius*Math.cos(theta)
	    let y = radius*Math.sin(theta)
	    points.push(add(v2(x, y), center))
	    theta += inc
	}
	let x = radius*Math.cos(0)
	let y = radius*Math.sin(0)
	points.push(add(v2(x, y), center))
	return points
    }

    drawCircle(ident, center, radius, strokeColor, fill=false, fillColor=[0,0,0,1], strokeWidth=this.lineWidth) {

	let name = "object_line_" + ident.toString()

	let hot = false
	let active = false
	
	let points = this.getPoints(center, radius)
	
	if(this.polyUnderMouse(points)) {
	    hot = true
	    if(this.mouseDown) {
		active = true
	    }
	} 
	
	if(hot) {
	    // color = this.hotColor
	    fill = true
	}

	
	let gl = this.gl

	let vertices = []
	let num_indices = 0



	if(fill) {
	    vertices = points.map((p) => {
		return [p.x, p.y, 0.0, 1.0].concat(fillColor)
	    })
	    vertices = this.flatten(vertices)
	    num_indices = points.length + 1

	    if(this.glData.length < vertices.length) {
		this.glData = new Float32Array(vertices.length)
	    }

	    let data = this.glData
	    let FSIZE = data.BYTES_PER_ELEMENT

	    data.set(vertices)

	    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
	    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
	    gl.enableVertexAttribArray(a_Position)
	    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

	    let a_Color = gl.getAttribLocation(gl.program, "a_Color")
	    gl.enableVertexAttribArray(a_Color)
	    gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)


	    gl.drawArrays(gl.TRIANGLE_FAN, 0, num_indices)
	}

	vertices = this.makeLineBuf(points, strokeColor, strokeWidth)
	num_indices = 2*(points.length)

	if(this.glData.length < vertices.length) {
	    this.glData = new Float32Array(vertices.length)
	}

	let data = this.glData
	let FSIZE = data.BYTES_PER_ELEMENT

	data.set(vertices)

	gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
	let a_Position = gl.getAttribLocation(gl.program, "a_Position")
	gl.enableVertexAttribArray(a_Position)
	gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

	let a_Color = gl.getAttribLocation(gl.program, "a_Color")
	gl.enableVertexAttribArray(a_Color)
	gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)


        gl.drawArrays(gl.TRIANGLE_STRIP, 0, num_indices)

	return hot

    }


    drawPoly(ident, points, color, fill=false) {

	let name = "object_line_" + ident.toString()

	let hot = false
	let active = false
	
	if(this.polyUnderMouse(points)) {
	    hot = true
	    if(this.mouseDown) {
		active = true
	    }
	}
	
	if(hot) {
	    // color = this.hotColor
	    fill = true
	}

	points.push(points[0])
	let vertices = []
	let num_indices = 0

	if(fill) {
	    let gl = this.gl
	    vertices = points.map((p) => {
		return [p.x, p.y, 0.0, 1.0].concat(color)
	    })
	    vertices = this.flatten(vertices)
	    num_indices = points.length
	    
	    if(this.glData.length < vertices.length) {
		this.glData = new Float32Array(vertices.length)
	    }
	    
	    let data = this.glData

	    let FSIZE = data.BYTES_PER_ELEMENT


	    data.set(vertices)

	    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
	    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
	    gl.enableVertexAttribArray(a_Position)
	    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

	    let a_Color = gl.getAttribLocation(gl.program, "a_Color")
	    gl.enableVertexAttribArray(a_Color)
	    gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)


	    gl.drawArrays(gl.TRIANGLE_STRIP, 0, num_indices)
	}

	for(let i = 0; i<points.length-1; i++) {
	    let p1 = points[i]
	    let p2 = points[i+1]
	    this.drawLine(ident, p1, p2, color, false)
	}
	
	return hot
    }



}


/*************************************

           Event Listeners

*************************************/

function onMouseMove( event ) {
    this.canvasRect = this.gl.canvas.getBoundingClientRect()
    let canvasRect = this.canvasRect
    let size = this.size
    
    let xgood = event.clientX > canvasRect.left && event.clientX < canvasRect.right
    let ygood = event.clientY > canvasRect.top  && event.clientY < canvasRect.bottom

    if(xgood && ygood) {
	event.preventDefault();
	this.mouseInCanvas = true
	this.mouse.x = ((event.clientX - canvasRect.left) / size ) * 2 - 1;
	this.mouse.y = - ( (event.clientY - canvasRect.top) / size ) * 2 + 1;
    }
    else {
	this.mouseInCanvas = false
	this.mouse.x = -10000000
	this.mouse.y = -10000000
    }
}

function onResize( event ) {
    this.canvasRect = this.gl.canvas.getBoundingClientRect()
    let width = document.body.clientWidth
    width = width < 600 ? width : width*0.65
    this.size = Math.min(width, window.innerHeight)
    let realToCSSPixels = window.devicePixelRatio
    let drawSize = Math.floor(this.size * realToCSSPixels)
    this.gl.canvas.style.width = this.size + "px";
    this.gl.canvas.style.height = this.size + "px"; 
}

/*************************************

        Geometric Predicates

*************************************/


function v2(x, y) {
    return {x:x, y:y}
}

function dot(v1, v2) {
    return (v1.x*v2.x)+(v1.y*v2.y)
}

function add(v1, v2) {
    return {
	x: v1.x+v2.x,
	y: v1.y+v2.y
    }
}

function sub(v1, v2) {
    return {
	x: v1.x-v2.x,
	y: v1.y-v2.y
    }
}

function normsq(v) {
    return dot(v,v)
}

function norm(v) {
    return Math.sqrt(normsq(v))
}

function scale(v, c) {
    return v2(v.x*c, v.y*c)
}

function normal(v) {
    // Return the unit vector normal to v
    let n = norm(v)
    if(n == 0.0)
	return v2(0,0)
    v = scale(v, 1.0/norm(v))
    return v2(v.y, -v.x)
}



