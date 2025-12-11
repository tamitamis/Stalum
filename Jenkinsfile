pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: alumni-portal-builder
spec:
  containers:
  - name: python
    image: python:3.11-slim
    command:
    - cat
    tty: true
  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command:
    - cat
    tty: true
    resources:
      limits:
        memory: "512Mi"
      requests:
        memory: "128Mi"
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
    tty: true
    securityContext:
      runAsUser: 0
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
'''
        }
    }

    environment {
        // Your Specific Configs
        NEXUS_URL = 'nexus.imcc.com'
        NEXUS_REPO = 'my-repository' 
        IMAGE_NAME = 'alumni-portal'
        NAMESPACE = '2401192' // Using your ID as namespace
    }

    stages {
        stage('Install Dependencies & Test') {
            steps {
                container('python') {
                    sh '''
                        pip install -r requirements.txt
                        pip install gunicorn whitenoise
                        python manage.py test
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        # Wait for docker daemon to be ready
                        sleep 5
                        docker build -t ${IMAGE_NAME}:latest .
                        docker image ls
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    // Using the credentials you provided
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=alumni_portal_project \
                            -Dsonar.host.url=http://sonarqube.imcc.com/ \
                            -Dsonar.login=student \
                            -Dsonar.password=Imccstudent@2025 \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/venv/**,**/migrations/**,**/static/** \
                            -Dsonar.python.version=3.11
                    '''
                }
            }
        }

        stage('Login & Push to Nexus') {
            steps {
                container('dind') {
                    script {
                        // Login
                        sh "docker login -u student -p Imcc@2025 http://${NEXUS_URL}"
                        
                        // Tag
                        sh "docker tag ${IMAGE_NAME}:latest ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:latest"
                        
                        // Push
                        sh "docker push ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    script {
                        // Create the deployment YAML dynamically or read from file
                        // Here we create the namespace and apply the file we will create next
                        sh """
                            kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            kubectl apply -f k8s-deployment/alumni-deployment.yaml -n ${NAMESPACE}
                            
                            # Wait for rollout to finish
                            kubectl rollout status deployment/alumni-portal -n ${NAMESPACE}
                        """
                    }
                }
            }
        }
    }
}