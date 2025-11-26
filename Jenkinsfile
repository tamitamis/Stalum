pipeline {
    agent any

    environment {
        // --- YOUR COLLEGE CONFIGURATION ---
        
        // Nexus Settings
        NEXUS_URL = 'nexus.imcc.com' 
        // NOTE: If Docker push fails, try adding port :8082 or :8083 to this URL
        NEXUS_REPO = '2401192' 
        IMAGE_NAME = 'alumni-portal'
        
        // Nexus Credentials (student / Imcc@2025)
        NEXUS_USER = 'student'
        NEXUS_PASS = 'Imcc@2025'

        // SonarQube Settings are read from sonar-project.properties automatically
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // This uses the SonarScanner tool installed on the college server
                script {
                    def scannerHome = tool 'SonarScanner' 
                    sh "${scannerHome}/bin/sonar-scanner"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the image locally on Jenkins
                    sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                script {
                    // 1. Log in to Nexus
                    // We wrap the URL in http:// because your college uses http
                    sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} http://${NEXUS_URL}"
                    
                    // 2. Tag the image for Nexus
                    sh "docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    
                    // 3. Push the image
                    sh "docker push ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}"
                }
            }
        }
    }
}