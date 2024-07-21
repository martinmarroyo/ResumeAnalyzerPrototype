# SkillSync Analyzer Prototype

[Try SkillSync Analyzer here!](https://skillsyncanalyzer-0gtiy8v6.b4a.run/)

This prototype is a submission for the lablab.ai Llama3 hackathon. The purpose of this application is to help job seekers better craft their resume or upskill for the roles they desire. Users can submit their resume, job description, and email address using our UI, then they will receive a full analysis of their resume to the email provided that includes:

- A gap analysis between the current resume and what is asked on the job description
- Suggestions for upskilling to fill the gaps identified
- Overall feedback on the resume and where it can improve
- A list of potential interview questions to prepare for based on the role in the job description and the user's resume 

## Getting started

In order to build this, you need `Docker` installed on your system. Once you have that, you can move on to the next steps.

1. Build the image
   
   Inside of a terminal in the root directory of the project, run the following line:
   ```bash
   docker build -t resume_analyzer .
   ```
2. Build the container

   After the image is built, you can then run the container with the following command:

   ```bash
   docker run -d \
   --name resume_analyzer \
   --rm \
   -e TOGETHER_API_KEY="Your Together API key" \
   -e EMAIL_USER="Your email address" \
   -e EMAIL_PASSWORD="Your email password" \
   -p 5000:5000 \
   resume_analyzer
   ```
