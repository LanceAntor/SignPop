# SignPop

SignPop is an engaging and interactive learning app designed to help users master the American Sign Language (ASL) alphabet. Whether you're a beginner or looking to reinforce your skills, this app offers a fun and educational experience through step-by-step tutorials, visual demonstrations, and an exciting game mode to test your knowledge.

## Visual Demo

### Home Page
![Home Page Screenshot](static/signpop_screenshots/homepage.jpg)
*Application home page with navigation options*

### Tutorial Mode
![Tutorial Mode Screenshot](static/signpop_screenshots/tutorial.jpg)
*Tutorial mode showing reference images and real-time hand detection*

### SignPop Game
![SignPop Game Screenshot](static/signpop_screenshots/gamemode.jpg)
*Game mode with falling letters that players match with hand signs*


## Features

- **Tutorial Mode**: Interactive learning environment with real-time hand gesture recognition
- **SignPop Game**: Fun game where users "pop" falling letters by performing the correct hand sign
- **Real-time Detection**: Advanced computer vision for accurate hand sign recognition
- **User-friendly Interface**: Clean and intuitive design with interactive elements

## Installation

```bash
# Clone the repository
git clone https://github.com/LanceAntor/SignPop.git
cd SignLanguageAlphabet

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

```
# Usage
The tutorial mode allows users to:
- **Viiew reference images for each ASL letter**
- **Practice hand signs with real-time feedbackr**
- **Toggle camera on/off for privacyr**

In the game mode, players: 
- **Form hand signs to match falling letters**
- **Score points for correct signsr**
- **Track progress with the score system**
- **Manage lives to continue playing**

## Built With

- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
- ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
- ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
- ![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
- ![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
- ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
- ![Font Awesome](https://img.shields.io/badge/Font%20Awesome-528DD7?style=for-the-badge&logo=fontawesome&logoColor=white)

# Acknowledgement

- **[Flask](https://flask.palletsprojects.com/)**: The lightweight web framework that powers the project.
- **[OpenCV](https://opencv.org/)**: For real-time computer vision and camera handling.
- **[TensorFlow](https://www.tensorflow.org/)**: For the machine learning model that powers sign detection.
- **[cvzone](https://github.com/cvzone/cvzone)**: For simplified computer vision and hand tracking utilities.
- **[NumPy](https://numpy.org/)**: For numerical operations and array handling in image processing.
- **[Font Awesome](https://fontawesome.com/)**: For offering free and high-quality icons.
- **[jQuery](https://jquery.com/)**: For simplifying DOM manipulation and AJAX interactions.
- **[ASL University](https://www.lifeprint.com/)**: For reference materials on American Sign Language.
- **[Kaggle ASL Dataset](https://www.kaggle.com/grassknoted/asl-alphabet)**: For providing training data for the sign recognition model.
