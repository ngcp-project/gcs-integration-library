from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)
#app.config["CACHE_TYPE"] = "null"

@app.route('/')
def index(): return """
<!DOCTYPE html>

<head>
    <title>PiCam Server</title>
    <link rel="stylesheet" href='../static/style.css'/>
</head>

<body>
    
        <h1>PiCam Live Streaming</h1>
        
        <div class="img-container">
            <img src="http://localhost:5000/video_feed">
        </div>
        <footer>AranaCorp All right reserved &#169;</footer>
        
</body>

</html>    
"""
  # Camera 1
def gen():
    """Video streaming generator function."""
    vs = cv2.VideoCapture("/dev/video0")
    while True:
        ret,frame=vs.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame=jpeg.tobytes()
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
    # vs.release()
    # cv2.destroyAllWindows() 

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__': 
    app.run(host='0.0.0.0', port =5000, debug=True, threaded=True)
