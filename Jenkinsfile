pipeline {
    agent any

    environment {
        // --- YOUR COLLEGE CONFIGURATION ---
        
        // Nexus Settings
        NEXUS_URL = 'nexus.imcc.com' 
        NEXUS_REPO = '2401192' // Make sure this matches your repo name!
        IMAGE_NAME = 'alumni-portal'
        
        // Nexus Credentials
        NEXUS_USER = 'student'
        NEXUS_PASS = 'Imcc@2025'

        // --- FIX FOR CRASHING AGENT ---
        // Limit SonarScanner to 256MB RAM so it doesn't kill the container
        SONAR_SCANNER_OPTS = '-Xmx256m'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner' 
                    sh "${scannerHome}/bin/sonar-scanner"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                script {
                    sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} http://${NEXUS_URL}"
                    sh "docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    sh "docker push ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}"
                }
            }
        }
    }
}