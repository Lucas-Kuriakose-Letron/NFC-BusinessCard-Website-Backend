from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from groq import Groq
from Emailer import send_email, Emailer
from vCard_generator import ContactCardGenerator
from JsonDataManager import DataManager

#initialization
app = Flask(__name__)
CORS(app)
dataManager = DataManager()
downloads = dataManager.load("downloads.json", [])
meetings  = dataManager.load("meetings.json",  [])
settings = dataManager.load("settings.json", {
    "name":      "Client Name",
    "company":   "",
    "bio":       "Stuff about me and my business.",
    "photo_url": "",
    "pricing":   "Contact us for pricing information.",
    "locations": {
        "suffolk": "631-123-4567",
        "nassau":  "516-123-4567",
        "NJ":      "123-456-7890"
    }
})
chatbotSettings = dataManager.load("chatbot.json", {
    "script": "You are a helpful assistant for a real estate agent. Answer questions professionally.",
    "faq":    ""
})

#routes/functions
#settings
@app.route("/profile")
def profile():
    return jsonify(settings)

@app.route("/chatbotSettings")
def get_chatbot_config():
    return jsonify(chatbotSettings)

#numbers and appointments
@app.post("/submitNumber")
def submitNumber():
    data = request.get_json()
    newContact = {
        "name":     data.get("name"),
        "phone":    data.get("phone"),
        "location": data.get("location"),
        "message":  data.get("message", "")
    }
    downloads.append(newContact)
    dataManager.save("downloads.json", downloads)
    return jsonify({"message": "Number saved"})


@app.post("/requestAppointment")
def requestAppointment():
    data = request.get_json()
    newAppointment = {
        "name":   data.get("name"),
        "phone":  data.get("phone"),
        "email":  data.get("email"),
        "date":   data.get("date"),
        "time":   data.get("time"),
        "status": "pending"
    }
    meetings.append(newAppointment)
    dataManager.save("meetings.json", meetings)
    return jsonify({"success": True})


@app.route("/downloadClientContact")
def downloadClientContact():
    region    = request.args.get("region")
    locations = settings.get("locations", {})
    number    = locations.get(region)

    if not number:
        return jsonify({"error": "Region not found: " + str(region)}), 404

    generator = ContactCardGenerator()
    vcardText = generator.generate_vcard(
        name=settings.get("name", "Client"),
        phone=number,
        company=settings.get("company", "")
    )
    return Response(
    vcardText,
    mimetype="text/vcard",
    headers={ "Content-Disposition": "attachment; filename=client.vcf" }
)


#admin routes
@app.route("/admin/numbers")
def get_numbers():
    return jsonify(downloads)


@app.route("/admin/appointments")
def get_appointments():
    return jsonify(meetings)


@app.route("/admin/download/<int:index>")
def downloadSubmittedContact(index):
    if index >= len(downloads):
        return jsonify({"error": "Not found"}), 404

    person    = downloads[index]
    generator = ContactCardGenerator()
    vcardText = generator.generate_vcard(
        name=person.get("name", "Unknown"),
        phone=person.get("phone", ""),
        company=""
    )
    return Response(
        vcardText,
        mimetype="text/vcard",
        headers={ "Content-Disposition": "attachment; filename=contact.vcf" }
    )


@app.post("/admin/updateAppointment")
def updateAppointment():
    data   = request.get_json()
    index  = data.get("index")
    status = data.get("status")

    if index is None or index >= len(meetings):
        return jsonify({"error": "Invalid index"}), 400

    meetings[index]["status"] = status
    dataManager.save("meetings.json", meetings)

    appointment  = meetings[index]
    emailAddress = appointment.get("email")

    if status == "approved" and emailAddress:
        send_email(
            to_address=emailAddress,
            subject="Appointment Confirmed",
            body=(
                "Hi " + appointment.get("name", "there") + ",\n\n"
                "Your appointment for "
                + appointment.get("date") + " at " + appointment.get("time") +
                " has been confirmed.\n\n"
                "Looking forward to meeting with you.\n\n"
                "— " + settings.get("name", "The Team")
            )
        )

    if status == "denied" and emailAddress:
        send_email(
            to_address=emailAddress,
            subject="Appointment Request Update",
            body=(
                "Hi " + appointment.get("name", "there") + ",\n\n"
                "Unfortunately your appointment request for "
                + appointment.get("date") + " at " + appointment.get("time") +
                " could not be accommodated at this time.\n\n"
                "Please feel free to request a new time. I will try to reach out directly to plan a meeting.\n\n"
                "— " + settings.get("name", "The Team")
            )
        )

    return jsonify({"success": True})


@app.post("/admin/updateAll")
def updateAll():
    global settings, chatbotSettings

    data = request.get_json()

    newSettings = data.get("settings")
    newChatbot  = data.get("chatbot")

    if newSettings:
        settings = newSettings
        dataManager.save("settings.json", settings)

    if newChatbot:
        chatbotSettings = newChatbot
        dataManager.save("chatbot.json", chatbotSettings)

    return jsonify({"success": True})


@app.route("/admin/email-config")
def get_email_config():
    return jsonify({"sender_email": Emailer.sender_email})


@app.post("/admin/updateEmail")
def updateEmail():
    data        = request.get_json()
    newEmail    = data.get("sender_email", "").strip()
    newPassword = data.get("sender_password", "").strip()

    if newEmail:
        Emailer.sender_email = newEmail

    if newPassword:
        Emailer.sender_password = newPassword

    return jsonify({"success": True})

#chat
@app.post("/chat")
def chat():
    userMessage = request.get_json().get("message", "")
    script = chatbotSettings.get("script", "You are a helpful assistant for me.")
    faq    = chatbotSettings.get("faq", "")
    systemPrompt = script
    if faq:
        systemPrompt = systemPrompt + "\n\nFAQ:\n" + faq
    try:
        client = Groq()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user",   "content": userMessage}
            ]
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as error:
        return jsonify({"reply": "Error: " + str(error)})

#run the app
if __name__ == "__main__":

    app.run(debug=True)
