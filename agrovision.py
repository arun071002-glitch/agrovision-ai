from flask import Flask, render_template_string, request
from PIL import Image
import numpy as np
import random
import base64
from io import BytesIO

app = Flask(__name__)

# -------------------------------
# AI Crop Analysis
# -------------------------------
def analyze_crop(image):
    image = image.resize((224, 224))
    img_array = np.array(image)

    red = np.mean(img_array[:, :, 0])
    green = np.mean(img_array[:, :, 1])

    veg_index = (green - red) / (green + red + 1)

    if green < 70:
        return "Not a Crop", 0, 0

    if veg_index > 0.12:
        return "Healthy Crop", random.randint(75, 95), random.randint(5, 20)
    elif veg_index > 0:
        return "Moderate Stress", random.randint(45, 70), random.randint(30, 55)
    else:
        return "High Pest Risk", random.randint(20, 40), random.randint(65, 95)

# -------------------------------
# Soil Simulation
# -------------------------------
def soil_analysis():
    moisture = random.randint(30, 80)
    ph = round(random.uniform(5.5, 8.0), 1)
    nitrogen = random.randint(30, 90)
    return moisture, ph, nitrogen

# -------------------------------
# Weather Simulation based on location
# -------------------------------
def weather_analysis(location):

    # simulate based on location name
    seed = sum(ord(c) for c in location)
    random.seed(seed)

    temperature = random.randint(20, 38)
    humidity = random.randint(40, 90)
    rainfall = random.randint(0, 30)
    wind = random.randint(5, 25)

    return temperature, humidity, rainfall, wind

# -------------------------------
# Pest Advice
# -------------------------------
def pest_advice(risk):
    if risk < 25:
        return "Low risk. Maintain monitoring."
    elif risk < 60:
        return "Apply neem oil spray and inspect leaves weekly."
    else:
        return "Immediate treatment required: organic pesticide + isolate affected plants."

# -------------------------------
# HTML TEMPLATE
# -------------------------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>AI Crop Monitoring</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body {

margin:0;
font-family:'Segoe UI';
background:
linear-gradient(135deg,#0f2027,#203a43,#2c5364,#00c9a7);
background-size:400% 400%;
animation:bg 15s infinite;
color:white;

}

@keyframes bg{
0%{background-position:0%}
50%{background-position:100%}
100%{background-position:0%}
}

.header{
background:rgba(0,0,0,0.4);
padding:20px;
font-size:32px;
font-weight:bold;
text-align:center;
backdrop-filter:blur(10px);
}

.container{
width:95%;
max-width:1300px;
margin:auto;
padding:20px;
}

.card{

background:rgba(255,255,255,0.08);
backdrop-filter:blur(15px);
padding:20px;
margin:15px;
border-radius:15px;
box-shadow:0 10px 30px rgba(0,0,0,0.5);

}

.grid{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(350px,1fr));
}

button{

background:linear-gradient(45deg,#00c9a7,#00ffcc);
border:none;
padding:12px 20px;
border-radius:10px;
font-weight:bold;
cursor:pointer;

}

button:hover{
transform:scale(1.05);
}

input{
padding:10px;
border-radius:10px;
border:none;
margin:5px;
}

video,img{
width:300px;
border-radius:10px;
}

canvas{
background:white;
border-radius:10px;
padding:10px;
}

</style>

</head>

<body>

<div class="header">
🌱 AI Powered Crop Monitoring System
</div>

<div class="container">

<div class="card">

<form method="POST" enctype="multipart/form-data">

<input type="text" name="location" placeholder="Enter Location" required>
<br>

<input type="file" name="image">
<br><br>

<button type="submit">Analyze</button>

</form>

<br>

<video id="video" autoplay></video>
<br>

<button onclick="capture()">Capture</button>

<form method="POST" id="cameraForm">
<input type="hidden" name="camera_image" id="camera_image">
<input type="hidden" name="location" id="camera_location">
</form>

</div>

{% if result %}

<div class="grid">

<div class="card">
<h3>Crop Result</h3>
<img src="{{ image_data }}">
<p>{{ health }}</p>
<p>Pest Risk: {{ pest_risk }}%</p>
</div>

<div class="card">
<h3>Crop Analysis</h3>
<canvas id="cropChart"></canvas>
</div>

<div class="card">
<h3>Soil Analysis</h3>
<canvas id="soilChart"></canvas>
</div>

<div class="card">
<h3>Weather Analysis ({{ location }})</h3>
<canvas id="weatherChart"></canvas>
</div>

<div class="card">
<h3>Advice</h3>
<p>{{ advice }}</p>
</div>

</div>

<script>

new Chart(document.getElementById('cropChart'),{
type:'doughnut',
data:{
labels:['Health','Pest Risk'],
datasets:[{
data:[{{ health_score }},{{ pest_risk }}]
}]
}
})

new Chart(document.getElementById('soilChart'),{

type:'radar',

data:{
labels:['Moisture','pH','Nitrogen'],
datasets:[{
data:[{{ moisture }},{{ ph }},{{ nitrogen }}]
}]
}

})

new Chart(document.getElementById('weatherChart'),{

type:'bar',

data:{
labels:['Temperature','Humidity','Rainfall','Wind'],
datasets:[{
label:'Weather Condition',
data:[{{ temperature }},{{ humidity }},{{ rainfall }},{{ wind }}]
}]
}

})

</script>

{% endif %}

</div>

<script>

const video=document.getElementById('video');

navigator.mediaDevices.getUserMedia({video:true})
.then(stream=>video.srcObject=stream);

function capture(){

const canvas=document.createElement('canvas');
canvas.width=video.videoWidth;
canvas.height=video.videoHeight;

canvas.getContext('2d').drawImage(video,0,0);

const data=canvas.toDataURL();

document.getElementById('camera_image').value=data;
document.getElementById('camera_location').value=
document.querySelector("input[name='location']").value;

document.getElementById('cameraForm').submit();

}

</script>

</body>
</html>
"""

# -------------------------------
# ROUTE
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        location = request.form.get("location","Unknown")

        if "camera_image" in request.form and request.form["camera_image"]!="":

            data=request.form["camera_image"]
            header,encoded=data.split(",")
            image=Image.open(BytesIO(base64.b64decode(encoded)))
            image_data=data

        elif "image" in request.files:

            file=request.files["image"]
            image=Image.open(file)

            buffered=BytesIO()
            image.save(buffered,format="PNG")

            image_data="data:image/png;base64,"+base64.b64encode(buffered.getvalue()).decode()

        else:

            return render_template_string(HTML,result=False)

        health,health_score,pest_risk=analyze_crop(image)
        moisture,ph,nitrogen=soil_analysis()

        temperature,humidity,rainfall,wind=weather_analysis(location)

        advice=pest_advice(pest_risk)

        return render_template_string(

        HTML,

        result=True,

        image_data=image_data,
        health=health,
        health_score=health_score,
        pest_risk=pest_risk,

        moisture=moisture,
        ph=ph,
        nitrogen=nitrogen,

        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall,
        wind=wind,

        location=location,

        advice=advice

        )

    return render_template_string(HTML,result=False)

# -------------------------------
# RUN
# -------------------------------
if __name__=="__main__":
    app.run(debug=True)
