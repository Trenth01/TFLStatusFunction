# Alexa Tube Status Skill (TfL API Integration)

This project provides a custom Alexa skill powered by an AWS Lambda function written in Python. It fetches real-time status updates for London Underground lines using the Transport for London (TfL) API and responds to voice queries about tube line disruptions.

## 🛠 Overview

The Lambda function:

- Queries the TfL API for current status of all London Underground lines.
- Responds to user requests (via Alexa) for specific line statuses, or defaults to a few key lines (Victoria, Circle, District).
- Uses fuzzy matching to recognize approximate line names (e.g. "piccadily" ➝ "Piccadilly").
- Returns a speech-friendly response that Alexa can read back to the user.

## 🧾 Example Usage

**User:** "Alexa, ask Tube Status how the Central line is doing."  
**Alexa:** "The Central line has severe delays due to a signal failure at Liverpool Street."

---

## 📁 Repository Structure
├── lambda_function.py # Main Python code for the Lambda function ├── README.md # This file

---

## ⚙️ Setting Up the Alexa Skill with AWS Lambda

Follow these steps to deploy this skill and connect it to your Alexa device:

### 1. **Create an AWS Lambda Function**

1. Go to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Click **Create function** > **Author from scratch**
3. Name your function, e.g., `AlexaTubeStatus`
4. Choose **Python 3.9+** as the runtime
5. Create or assign an existing IAM role with basic Lambda execution permissions
6. In the Lambda editor:
   - Upload `lambda_function.py` or paste the code into the inline editor
7. Under **Runtime settings**, set the handler to:
    lambda_function.lambda_handler


---

### 2. **Set Up the Alexa Custom Skill**

1. Go to the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click **Create Skill**
3. Choose a name (e.g. `Tube Status`)
4. Choose **Custom** skill
5. Choose **Alexa-Hosted (Node.js)** if you're testing, or **Provision your own** if deploying via AWS Lambda

#### Define an Intent

1. In the **Interaction Model** > **Intents**, create a new intent called `GetLineStatusIntent`
2. Add sample utterances like:
- "How is the {line} line"
- "Is the {line} line delayed"
- "Status of the {line} line"
- "How are the trains"
3. Add a **slot** named `line` of type `AMAZON.LITERAL` or define a custom slot type listing all Tube lines.

#### Link to Lambda

1. Go to **Endpoint** section of the Alexa Developer Console
2. Choose **AWS Lambda ARN (Amazon Resource Name)**
3. Paste your Lambda ARN (from AWS Lambda Console)
4. Choose the region where your Lambda function is deployed

---

## 🔍 Notes

- This function uses TfL’s public API, which does not require an API key.
- Make sure your Lambda function has network access to the public internet.
- You can improve line recognition with a custom slot type listing all line names:
```txt
Bakerloo
Central
Circle
District
Hammersmith & City
Jubilee
Metropolitan
Northern
Piccadilly
Victoria
Waterloo & City


---

🧪 Testing
Use the Alexa Developer Console's Test tab to simulate interactions and verify the skill’s responses.

---

📋 License
This project is open source and available under the MIT License.
