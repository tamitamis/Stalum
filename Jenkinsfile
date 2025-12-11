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
        IMAGE_REGISTRY = '127.0.0.1:30085'
        IMAGE_PATH = '2401192-project/alumni-portal'
        NAMESPACE = '2401192'
    }

    stages {
        stage('Install Dependencies & Test') {
            steps {
                container('python') {
                    sh '''
                        pip install -r requirements.txt
                        python manage.py test
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        sleep 15
                        docker build -t alumni-portal:latest .
                        docker image ls
                    '''
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

        stage('Login to Docker Registry') {
            steps {
                container('dind') {
                    sh 'docker --version'
                    sh 'sleep 10'
                    // Using the registry IP/Port directly as requested
                    sh "docker login ${IMAGE_REGISTRY} -u student -p Imcc@2025"
                }
            }
        }

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
                        dir('k8s-deployment') {
                            sh """
                                # Create namespace if not exists
                                kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                                
                                # Apply deployment and ingress
                                kubectl apply -f alumni-deployment.yaml -n ${NAMESPACE}

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