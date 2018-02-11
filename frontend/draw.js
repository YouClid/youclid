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
    constructor(renderFunc) {
	this.mouse = {x:1000, y:10000}
	this.mousedown = false
	this.mouseup = true

	this.gl = null
	this.glData = null

	this.drawn = {}

	this.size = Math.min(window.innerWidth*0.65, window.innerHeight)

	this.canvasRect = null

	this.hot = {}
	this.active = null

	this.render = renderFunc

	this.init()
    }
    
    init() {
	
	
	let canvas = document.createElement('canvas')
	document.body.appendChild( canvas )

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

	gl.lineWidth(3.0)

	// Register listeners
	document.addEventListener( 'mousemove', onMouseMove.bind(this));
	window.addEventListener( 'resize', onResize.bind(this));
    
	this.update()
    }

    update() {
	let gl = this.gl
	gl.clearColor(0.0, 0.0, 0.0, 1.0)
	gl.clear(gl.COLOR_BUFFER_BIT)
    
	this.render(this) // Defined by user

    }

    setRender(render) {
	this.render = render
	this.update()
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
	return this.dist(this.mouse, center) < 0.06
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
	return d < 0.05
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
        // create a circular point (filled in) of radius 0.01
        return this.drawCircle(ident, point, 0.01, color, true)
    }


    drawLine(ident, p1, p2, color) {

	let name = "object_line_" + ident.toString()

	let hot = this.isHot(name)
    
	if(this.lineUnderMouse(p1, p2)) {
	    if(!hot) {
		if(this.active === null) {
		    this.hot[name] = true
		    hot = true
		}
	    }
	} else {
	    if(hot) {
		this.hot[name] = false
		hot = false
	    }
	}
    
	if(hot) {
	    color = [1.0, 1.0, 0, 1.0] // Yellow
	}

    
	let gl = this.gl
    
	let data = this.glData

	let FSIZE = data.BYTES_PER_ELEMENT

	let v1 = [
	    p1.x, p1.y, 0.0, 1.0
	]
	v1 = v1.concat(color)
	let v2 = [
	    p2.x, p2.y, 0.0, 1.0
	]
	v2 = v2.concat(color)

	let vertices = v1.concat(v2)
    
	data.set(vertices)

	gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
	let a_Position = gl.getAttribLocation(gl.program, "a_Position")
	gl.enableVertexAttribArray(a_Position)
	gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

	let a_Color = gl.getAttribLocation(gl.program, "a_Color")
	gl.enableVertexAttribArray(a_Color)
	gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)

	gl.drawArrays(gl.LINES, 0, 2)

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

    drawCircle(ident, center, radius, color, fill=false) {

	let name = "object_line_" + ident.toString()

	let hot = this.isHot(name)
	
	let points = this.getPoints(center, radius)
	
	if(this.polyUnderMouse(points)) {
	    if(!hot) {
		if(this.active === null) {
		    this.hot[name] = true
		    hot = true
		}
	    }
	} else {
	    if(hot) {
		this.hot[name] = false
		hot = false
	    }
	}
	
	if(hot) {
	    color = [1.0, 1.0, 0, 1.0] // Yellow
	}

	
	let gl = this.gl

	if(this.glData.length < (points.length * 8)) {
	    this.glData = new Float32Array(points.length * 8)
	}
	
	let data = this.glData

	let FSIZE = data.BYTES_PER_ELEMENT

	let vertices = points.map((p) => {
	    return [p.x, p.y, 0.0, 1.0].concat(color)
	})
	
	data.set(this.flatten(vertices))

	gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
	let a_Position = gl.getAttribLocation(gl.program, "a_Position")
	gl.enableVertexAttribArray(a_Position)
	gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

	let a_Color = gl.getAttribLocation(gl.program, "a_Color")
	gl.enableVertexAttribArray(a_Color)
	gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)

    if (fill === true)
        gl.drawArrays(gl.TRIANGLE_FAN, 0, points.length+1)
    else
        gl.drawArrays(gl.LINE_STRIP, 0, points.length+1)

	return hot

    }


    drawPoly(ident, points, color) {

	let name = "object_line_" + ident.toString()

	let hot = this.isHot(name)
	
	if(this.polyUnderMouse(points)) {
	    if(!hot) {
		if(this.active === null) {
		    this.hot[name] = true
		    hot = true
		}
	    }
	} else {
	    if(hot) {
		this.hot[name] = false
		hot = false
	    }
	}
	
	if(hot) {
	    color = [1.0, 1.0, 0, 1.0] // Yellow
	}

	
	let gl = this.gl

	if(this.glData.length < (points.length * 8)) {
	    this.glData = new Float32Array(points.length * 8)
	}
	
	let data = this.glData

	let FSIZE = data.BYTES_PER_ELEMENT

	points.push(points[0])

	let vertices = points.map((p) => {
	    return [p.x, p.y, 0.0, 1.0].concat(color)
	})
	
	data.set(this.flatten(vertices))

	gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
	let a_Position = gl.getAttribLocation(gl.program, "a_Position")
	gl.enableVertexAttribArray(a_Position)
	gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

	let a_Color = gl.getAttribLocation(gl.program, "a_Color")
	gl.enableVertexAttribArray(a_Color)
	gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)

	gl.drawArrays(gl.LINE_STRIP, 0, points.length)

	return hot
    }



}


/*************************************

           Event Listeners

*************************************/

function onMouseMove( event ) {
    let canvasRect = this.canvasRect
    let size = this.size
    
    let xgood = event.clientX > canvasRect.left && event.clientX < canvasRect.right
    let ygood = event.clientY > canvasRect.top  && event.clientY < canvasRect.bottom

    if(xgood && ygood) {
	this.mouse.x = ((event.clientX - canvasRect.left) / size ) * 2 - 1;
	this.mouse.y = - ( (event.clientY - canvasRect.top) / size ) * 2 + 1;

	this.update()
    }
}

function onResize( event ) {
    this.canvasRect = this.gl.canvas.getBoundingClientRect()
    this.size = Math.min(window.innerWidth*0.65, window.innerHeight)
    let realToCSSPixels = window.devicePixelRatio
    let drawSize = Math.floor(this.size * realToCSSPixels)
    this.gl.canvas.style.width = this.size + "px";
    this.gl.canvas.style.height = this.size + "px"; 
    this.update()
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



