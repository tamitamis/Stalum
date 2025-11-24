pipeline {
    agent any

    environment {
        // --- CONFIGURATION ---
        // Nexus Configuration
        NEXUS_URL = 'nexus.imcc.com'
        NEXUS_PROTOCOL = 'http://'
        NEXUS_REPO = 'alumni-docker-repo'  // CHECK THIS: Ask if there is a specific repo name
        IMAGE_NAME = 'alumni-portal'
        
        // Nexus Credentials
        NEXUS_USER = 'student'
        NEXUS_PASS = 'Imcc@2025'

        // SonarQube Tool Name (Must match what is configured in Jenkins Global Tools)
        SONAR_SCANNER_TOOL = 'SonarScanner' 
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    // We use the tool configured in Jenkins
                    def scannerHome = tool "${SONAR_SCANNER_TOOL}"
                    
                    // We pass the login details explicitly in case Jenkins isn't pre-configured
                    sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.host.url=http://sonarqube.imcc.com/ \
                        -Dsonar.login=student \
                        -Dsonar.password=Imccstudent@2025
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the image tagged with the Nexus URL
                    // Note: We use the URL without http:// for the tag
                    sh "docker build -t ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${BUILD_NUMBER} ."
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                script {
                    // 1. Log in to Nexus
                    sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} ${NEXUS_PROTOCOL}${NEXUS_URL}"
                    
                    // 2. Push the image
                    sh "docker push ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}"
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}