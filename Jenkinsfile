pipeline {
    agent any

    environment {
        // --- CONFIGURATION ---
        
        // Nexus Settings
        NEXUS_URL = 'nexus.imcc.com' 
        NEXUS_REPO = 'my-repository' // Make sure this matches your repo name!
        IMAGE_NAME = 'alumni-portal'
        
        // Nexus Credentials
        NEXUS_USER = 'student'
        NEXUS_PASS = 'Imcc@2025'
        
        // SonarQube Token (Generate on sonarqube.imcc.com -> My Account -> Security)
        SONAR_TOKEN = 'squ_4bb9a27b54c82377276324092165aa2053f702da'

       
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
                    // We pass the token here so Jenkins can log in
                    sh "${scannerHome}/bin/sonar-scanner -Dsonar.token=${SONAR_TOKEN}"
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