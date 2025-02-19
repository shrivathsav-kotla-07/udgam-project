import google.generativeai as genai
import PIL.Image
genai.configure(api_key="AIzaSyBrebjwXquFDImuNrDqBjl6pw-n_Q5VhbU")
image_path = "time_table.jpg"
image = PIL.Image.open(image_path)
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(["make it in a structure text whole timetable so that if i make it in vector emmdings it should be understood by the llm i want only that json thing ", image])
timetable = response.text
print(timetable)