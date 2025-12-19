pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
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
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
    tty: true
    securityContext:
      runAsUser: 0
    env:
    - name: KUBECONFIG
      value: /kube/config
    volumeMounts:
    - name: kubeconfig-secret
      mountPath: /kube/config
      subPath: kubeconfig
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    volumeMounts:
    - name: docker-config
      mountPath: /etc/docker/daemon.json
      subPath: daemon.json
  volumes:
  - name: docker-config
    configMap:
      name: docker-daemon-config
  - name: kubeconfig-secret
    secret:
      secretName: kubeconfig-secret
'''
        }
    }

    environment {
        // Project Specific Configs
        // Project Specific Configs
        // Project Specific Configs
        IMAGE_REGISTRY = 'nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085'
        IMAGE_PATH = 'my-repository/stalum'
        NAMESPACE = '2401192'
    }

    stages {
        stage('Install Dependencies & Test') {
            steps {
                container('python') {
                    sh '''
                        pip install -r requirements.txt
                        cd app
                        python manage.py test
                    '''
                }
            }
        }

        stage('Login to Docker Registry') {
            steps {
                container('dind') {
                    sh 'docker --version'
                    // Check for docker daemon readiness
                    sh '''
                        timeout=60
                        while ! docker info > /dev/null 2>&1; do
                            if [ $timeout -le 0 ]; then
                                echo "Timed out waiting for Docker daemon"
                                exit 1
                            fi
                            echo "Waiting for docker daemon..."
                            sleep 1
                            timeout=$((timeout - 1))
                        done
                    '''
                    // Using the registry IP/Port directly as requested
                    sh "docker login ${IMAGE_REGISTRY} -u student -p Imcc@2025"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh "docker build -t alumni-portal:latest ."
                    sh "docker image ls"
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=alumni_portal_project \
                            -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
                            -Dsonar.login=student \
                            -Dsonar.password=Imccstudent@2025 \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/venv/**,**/migrations/**,**/static/** \
                            -Dsonar.python.version=3.11
                    '''
                }
            }
        }

        // Login stage moved to run before build

        stage('Build - Tag - Push') {
            steps {
                container('dind') {
                    sh "docker tag alumni-portal:latest ${IMAGE_REGISTRY}/${IMAGE_PATH}:latest"
                    sh "docker push ${IMAGE_REGISTRY}/${IMAGE_PATH}:latest"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                container('kubectl') {
                    script {
                        dir('k8s') {
                            sh """
                                # Create namespace if not exists
                                kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                                
                                # Apply deployment, service, ingress
                                kubectl apply -f . -n ${NAMESPACE}

                                # Wait for rollout
                                kubectl rollout status deployment/alumni-portal -n ${NAMESPACE}
                            """
                        }
                    }
                }
            }
        }
    }
}