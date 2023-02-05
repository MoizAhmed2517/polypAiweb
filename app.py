import yolov5
import cv2
import streamlit as st
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
import time
import base64
import tempfile
# __________________ POLYP MODEL ____________________

def detectPolyp(path):
    model = yolov5.load('model.pt')

    #set model parameters
    model.conf = 0.25  # NMS confidence threshold
    model.iou = 0.45  # NMS IoU threshold
    model.agnostic = False  # NMS class-agnostic
    model.multi_label = False  # NMS multiple labels per box
    model.max_det = 1000  # maximum number of detections per image

    img = path

    # results = model.predict(img)
    results = model(img, size=640)
    predictions = results.pred[0]
    # boxes = predictions[:, :4]  # x1, y1, x2, y2
    # scores = predictions[:, 4]
    # categories = predictions[:, 5]

    return predictions

def cv2_detect(imagePath):
    image = cv2.imread(imagePath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    detect = detectPolyp(image)

    predictions = [p.numpy() for p in detect]

    for prediction in predictions:
        x1, y1, x2, y2, conf, class_id = prediction
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
        cv2.putText(image, "Polyp:", (int(x2) + 10, int(y2) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 0, 0), 2)
        cv2.putText(image, str(round(float(conf), 2)), (int(x2) + 60, int(y2) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 0, 0), 1)

    return image

def create_pdf(pdf_file_name, path, name, gender, age):
    # Define the data for the table
    space = "                                                   "
    sapce2 = "                  "
    # space3 = "                  "
    # sapce4="                                                         "
    data = [["Name"+sapce2, name], ["Sex", gender+space], ["Age", age]]

    # result = [
    #             ['Serial#'+space3, 'Accuracy'+sapce4],
    #             ['1', '92%'],
    #             ['2', '91%'],
    #             ['3', '86%'],
    #           ]

    # Create a PDF file
    doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)

    # Create a style for the header text
    style = ParagraphStyle(name="Header", fontSize=16, alignment=1, textColor="#0B233C")

    # Create a paragraph for the header text
    header_text = Paragraph("AI Polyp Detector", style)

    # Create a result heading
    style2 = ParagraphStyle(name="Footer", fontSize=14, alignment=1, textColor="#0B233C")
    result_text = Paragraph("Results", style2)

    # Create a table from the data
    table = Table(data)
    # table2 = Table(result)

    # Set the width of the table to be the full width of the page
    table.width = letter
    # table2.width = letter

    # Add the table to the document

    # Add a border to the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 1), '#0B233C'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#ffffff'),
        ('FONT', (0, 0), (-1, 1), 'Times-Bold', 10, 12),
        ('FONT', (0, 1), (-1, -1), 'Courier', 8, 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, '#000'),
        ('BOX', (0, 0), (-1, -1), 0.25, '#000'),
        ('BACKGROUND', (0, 1), (-1, -1), '#bebebe'),
    ]))

    # table2.setStyle(TableStyle([
    #     ('BACKGROUND', (0, 0), (-1, 1), '#0B233C'),
    #     ('TEXTCOLOR', (0, 0), (-1, 0), '#ffffff'),
    #     ('FONT', (0, 0), (-1, 1), 'Times-Bold', 10, 12),
    #     ('FONT', (0, 1), (-1, -1), 'Courier', 8, 8),
    #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #     ('INNERGRID', (0, 0), (-1, -1), 0.25, '#000'),
    #     ('BOX', (0, 0), (-1, -1), 0.25, '#000'),
    #     ('BACKGROUND', (0, 1), (-1, -1), '#bebebe'),
    # ]))

    # Create a spacer between the header and the table
    spacer = Spacer(1, 20)

    # Load the image file
    image = Image(path, width=400, height=263)

    # Create a list of elements to add to the PDF document
    elements = [header_text, spacer, table, spacer, result_text, spacer, image]

    # Add the elements to the PDF document
    doc.build(elements)

# __________________ STREAMLIT UI APP ____________________

hide_st_style = """
    <style>
        MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# __________________ CREATING NAVBAR ____________________

st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktQOp6b7In1Zl3/Jr59b6EGGoI1aFkw7cmDA6j6gD" crossorigin="anonymous">', unsafe_allow_html=True)
st.markdown("""
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #0B233C;">
        <span class="navbar-brand h1 mx-3 fs-3" style="margin-bottom: -5px; font-weight: 500px; margin-top: -5px;">Polyp AI</span>
    </nav>
""", unsafe_allow_html=True)

# __________________ CREATING MAIN HEADING ____________________

st.title("Polyp Detector")
title_styling="""
<style>
#polyp-detector {
  text-align: center;
  font-size: 30px;
  font-weight: bold;
  margin-top: -65px;
  color: #0B233C;
}
</style>
"""
st.markdown(title_styling, unsafe_allow_html=True)

buttonStyle = """
    <style>
        div.stButton > button:first-child {
            height: 3em;
            width: 100%; 
        }
    </style>
"""
st.markdown(buttonStyle, unsafe_allow_html=True)

# __________________ CREATING INPUTS ____________________
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Enter your name")
with col2:
    gender = st.selectbox("Select your gender.", ('Male', 'Female', 'Binary'))

age = st.slider("How old are you?", 0, 130, 35)
image_file = st.file_uploader("Upload image for detection purposes")

if image_file is not None:
    size_mb = image_file.size/(1024**2)
    file_details = {
        "filename": image_file.name,
        "filetype": image_file.type,
        "filesize": "{:,.2f} MB".format(size_mb)
    }
    file_binary = image_file.getvalue()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
        image_path = f.name
        f.write(file_binary)

    if file_details['filetype'] in ('image/png', 'imgage/jpg', 'image/jpeg'):
        st.success("Valid Format!", icon="✅")
        btnCol1, btnCol2 = st.columns(2)

        with btnCol1:
            check_result = st.button("Check Results", type="primary")

        with btnCol2:
            if st.button("Generate Report", type="primary"):
                with st.spinner("Detecting Polyps in image....."):
                    image = cv2_detect(image_path)
                    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    cv2.imwrite('temp.jpg', img)
                with st.spinner("Creating pdf. Wait for pdf to be created..."):
                    time.sleep(0.5)
                    create_pdf('Result.pdf', 'temp.jpg', patient_name, gender, age)
                    st.success("Successfully created pdf")
                    with open('Result.pdf', "rb") as file:
                        file_content = file.read()
                        st.write("Download pdf from below link")
                        b64 = base64.b64encode(file_content).decode("utf-8")
                        st.markdown("<a href='data:application/pdf;base64,{}' download='report.pdf'>Download PDF</a>".format(b64), unsafe_allow_html=True)

        if check_result:
            with st.spinner("Detecting Polyps in image....."):
                image = cv2_detect(image_path)
                st.image(image, use_column_width=True)
            st.success("Successfully detected")

    else:
        st.error("Invalid Format! Only \'.jpeg\', \'.jpg\', \'.png\' format are accepted", icon="🚨")

